import uuid
from datetime import timedelta
from typing import Any, Optional, Union

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import gettext as _

from celery.result import AsyncResult
from model_utils.models import TimeStampedModel

from aleksis.core.mixins import ExtensibleModel
from aleksis.core.models import OAuthApplication, Person
from aleksis.core.util.pdf import process_context_for_pdf


class CardPrinterStatus(models.TextChoices):
    ONLINE = "online", _("Online")
    OFFLINE = "offline", _("Offline")
    WITH_ERRORS = "with_errors", _("With errors")
    NOT_REGISTERED = "not_registered", _("Not registered")

    @classmethod
    def get_color(cls, value):
        _colors = {
            CardPrinterStatus.ONLINE.value: "green",
            CardPrinterStatus.OFFLINE.value: "red",
            CardPrinterStatus.WITH_ERRORS.value: "orange",
            CardPrinterStatus.NOT_REGISTERED.value: "grey",
        }
        return _colors.get(value)

    @classmethod
    def get_icon(cls, value):
        _icons = {
            CardPrinterStatus.ONLINE.value: "mdi:printer-check",
            CardPrinterStatus.OFFLINE.value: "mdi:printer-off",
            CardPrinterStatus.WITH_ERRORS.value: "mdi:printer-alert",
            CardPrinterStatus.NOT_REGISTERED.value: "mdi:printer-search",
        }
        return _icons.get(value)

    @classmethod
    def get_label(cls, value):
        _labels = {x: y for x, y in cls.choices}
        return _labels.get(value)


class PrintStatus(models.TextChoices):
    REGISTERED = "registered", _("Registered")
    IN_PROGRESS = "in_progress", _("In progress")
    FINISHED = "finished", _("Finished")
    FAILED = "failed", _("Failed")


class CardPrinter(ExtensibleModel):
    SCOPE_PREFIX = "card_printer"
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"), blank=True)
    location = models.CharField(max_length=255, verbose_name=_("Location"), blank=True)

    status = models.CharField(
        max_length=255,
        verbose_name=_("Status"),
        choices=CardPrinterStatus.choices,
        default=CardPrinterStatus.NOT_REGISTERED,
    )
    status_text = models.TextField(verbose_name=_("Status text"), blank=True)
    last_seen_at = models.DateTimeField(verbose_name=_("Last seen at"), blank=True, null=True)

    oauth2_application = models.ForeignKey(
        to=OAuthApplication,
        on_delete=models.CASCADE,
        verbose_name=_("OAuth2 application"),
        blank=True,
        null=True,
        related_name="card_printers",
    )

    # Settings
    cups_printer = models.CharField(max_length=255, verbose_name=_("CUPS printer"), blank=True)
    generate_number_on_server = models.BooleanField(
        default=True, verbose_name=_("Generate card number on server")
    )
    card_detector = models.CharField(max_length=255, verbose_name=_("Card detector"), blank=True)

    def save(self, *args, **kwargs):
        if not self.oauth2_application:
            application = OAuthApplication(
                client_type=OAuthApplication.CLIENT_CONFIDENTIAL,
                authorization_grant_type=OAuthApplication.GRANT_CLIENT_CREDENTIALS,
                name=f"Card printer: {self.name}",
                redirect_uris="urn:ietf:wg:oauth:2.0:oob",
                allowed_scopes=[self.scope],
            )
            application.save()
            self.oauth2_application = application

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def status_label(self) -> str:
        """Return the verbose name of the status."""
        return CardPrinterStatus.get_label(self.status)

    @property
    def status_color(self) -> str:
        """Return a color for the status."""
        return CardPrinterStatus.get_color(self.status)

    @property
    def status_icon(self) -> str:
        """Return an iconify icon for the status."""
        return CardPrinterStatus.get_icon(self.status)

    def generate_config(self) -> dict[str, Any]:
        """Generate the configuration for the printer client."""
        config = {
            "base_url": settings.BASE_URL,
            "client_id": self.oauth2_application.client_id,
            "client_secret": self.oauth2_application.client_secret,
        }
        return config

    @property
    def config_filename(self) -> str:
        """Return the filename for the printer client configuration."""
        return f"card-printer-config-{self.pk}.json"

    def check_online_status(self):
        if (
            self.status
            not in (CardPrinterStatus.NOT_REGISTERED.value, CardPrinterStatus.OFFLINE.value)
            and self.last_seen_at
        ):
            if self.last_seen_at < timezone.now() - timedelta(minutes=1):
                self.status = CardPrinterStatus.OFFLINE.value
                self.save()

    @classmethod
    def check_online_status_for_all(cls, qs=None):
        if not qs:
            qs = cls.objects.all()
        for printer in cls.objects.all():
            printer.check_online_status()

    def get_next_print_job(self) -> Optional["CardPrintJob"]:
        if not self.generate_number_on_server:
            self.jobs.filter(
                (Q(card__pdf_file="") & ~Q(card__chip_number=""))
                | Q(status=PrintStatus.IN_PROGRESS)
            ).update(status=PrintStatus.FAILED)
            Card.objects.filter(
                jobs__in=self.jobs.filter(status=PrintStatus.FAILED), chip_number=""
            ).update(chip_number="")
        else:
            self.jobs.filter(status=PrintStatus.IN_PROGRESS).update(status=PrintStatus.FAILED)

        jobs = self.jobs.order_by("created").filter(status=PrintStatus.REGISTERED)
        if self.generate_number_on_server:
            jobs = jobs.filter(card__pdf_file__isnull=False)
        if jobs.exists():
            return jobs.first()
        return None

    @property
    def scope(self) -> str:
        """Return OAuth2 scope name to access PDF file via API."""
        return f"{self.SCOPE_PREFIX}_{self.id}"

    class Meta:
        verbose_name = _("Card printer")
        verbose_name_plural = _("Card printers")


class CardLayoutMediaFile(ExtensibleModel):
    media_file = models.FileField(upload_to="card_layouts/media/", verbose_name=_("Media file"))
    card_layout = models.ForeignKey(
        "CardLayout",
        on_delete=models.CASCADE,
        related_name="media_files",
        verbose_name=_("Card layout"),
    )

    def __str__(self):
        return self.media_file.name

    class Meta:
        verbose_name = _("Media file for a card layout")
        verbose_name_plural = _("Media files for card layouts")


class CardLayout(ExtensibleModel):
    BASE_TEMPLATE = """
    {{% extends "core/base_simple_print.html" %}}
    {{% load i18n static barcode %}}

    {{% block size %}}
      {{% with width={width} height={height} %}}
        {{{{ block.super }}}}
      {{% endwith %}}
    {{% endblock %}}

    {{% block extra_head %}}
      <style>
        {css}
      </style>
    {{% endblock %}}

    {{% block content %}}
      {template}
    {{% endblock %}}
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    template = models.TextField(verbose_name=_("Template"))
    css = models.TextField(verbose_name=_("Custom CSS"), blank=True)
    width = models.PositiveIntegerField(verbose_name=_("Width"), help_text=_("in mm"))
    height = models.PositiveIntegerField(verbose_name=_("Height"), help_text=_("in mm"))
    required_fields = ArrayField(models.TextField(), verbose_name=_("Required data fields"))

    def get_template(self) -> Template:
        template = self.BASE_TEMPLATE.format(
            width=self.width, height=self.height, css=self.css, template=self.template
        )
        return Template(template)

    def render(self, card: "Card"):
        t = self.get_template()
        context = card.get_context()
        processed_context = process_context_for_pdf(context)

        return t.render(Context(processed_context))

    def validate_template(self):
        try:
            t = Template(self.template)
            t.render(Context())
        except Exception as e:
            raise ValidationError(_("Template is invalid: {}").format(e))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Card Layout")
        verbose_name_plural = _("Card Layouts")


class Card(ExtensibleModel):
    person = models.ForeignKey(
        Person, models.CASCADE, verbose_name=_("Person"), related_name="cards"
    )
    chip_number = models.CharField(verbose_name=_("Chip Number"), blank=True, max_length=255)
    valid_until = models.DateField(verbose_name=_("Valid until"))
    deactivated = models.BooleanField(verbose_name=_("Deactivated"), default=False)

    layout = models.ForeignKey(
        CardLayout, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Card Layout")
    )
    pdf_file = models.FileField(
        verbose_name=_("PDF file"),
        blank=True,
        upload_to="cards/",
        validators=[FileExtensionValidator(["pdf"])],
    )

    @property
    def is_valid(self):
        return (
            self.valid_until >= timezone.now().date() and not self.deactivated and self.chip_number
        )

    def deactivate(self):
        self.deactivated = True
        self.save()

    def get_context(self):
        return {
            "person": self.person,
            "chip_number": self.chip_number,
            "valid_until": self.valid_until,
            "media_files": self.layout.media_files.all(),
        }

    def generate_pdf(self) -> Union[bool, AsyncResult]:
        from .tasks import generate_card_pdf

        if self.pdf_file:
            return True
        return generate_card_pdf.delay(self.pk)

    def print_card(self, printer: CardPrinter):
        if not self.layout:
            raise ValueError(_("There is no layout provided for the card."))
        job = CardPrintJob(card=self, printer=printer)
        job.save()
        if not self.chip_number and printer.generate_number_on_server:
            self.chip_number = str(self.generate_number())
            self.save()
        if self.chip_number:
            self.generate_pdf()
        return job

    def generate_number(self) -> int:
        return uuid.uuid1().int >> 32

    def __str__(self):
        if self.chip_number:
            return f"{self.person} ({self.chip_number})"
        return f"{self.person}"

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")


class CardPrintJob(TimeStampedModel, ExtensibleModel):
    printer = models.ForeignKey(
        CardPrinter, on_delete=models.CASCADE, verbose_name=_("Printer"), related_name="jobs"
    )
    card = models.ForeignKey(
        Card, on_delete=models.CASCADE, verbose_name=_("Card"), related_name="jobs"
    )

    status = models.CharField(
        max_length=255,
        verbose_name=_("Status"),
        choices=PrintStatus.choices,
        default=PrintStatus.REGISTERED,
    )
    status_text = models.TextField(verbose_name=_("Status text"), blank=True)

    class Meta:
        verbose_name = _("Card print job")
        verbose_name_plural = _("Card print jobs")
