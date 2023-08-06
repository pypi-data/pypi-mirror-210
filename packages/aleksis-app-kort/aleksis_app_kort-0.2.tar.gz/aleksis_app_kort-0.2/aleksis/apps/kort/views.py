import json

from django.contrib import messages
from django.db.models import Count, Q, QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.detail import DetailView, SingleObjectMixin

from django_tables2 import RequestConfig, SingleTableView, table_factory
from formtools.wizard.views import CookieWizardView
from guardian.shortcuts import get_objects_for_user
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.apps.kort.forms import (
    CardIssueFinishForm,
    CardIssueForm,
    CardLayoutForm,
    CardLayoutMediaFileFormSet,
    CardPrinterForm,
    PrinterSelectForm,
)
from aleksis.apps.kort.models import Card, CardLayout, CardPrinter, PrintStatus
from aleksis.apps.kort.tables import (
    CardLayoutTable,
    CardPrinterTable,
    CardTable,
    IssueCardPersonsTable,
)
from aleksis.core.mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from aleksis.core.models import Person
from aleksis.core.util.celery_progress import render_progress_page


class PrinterSelectMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["printers"] = CardPrinter.objects.all()
        context["printer_form"] = PrinterSelectForm()
        return context


class CardListView(PermissionRequiredMixin, RevisionMixin, PrinterSelectMixin, SingleTableView):
    """List view for all cards."""

    permission_required = "kort.view_cards_rule"
    template_name = "kort/card/list.html"
    model = Card
    table_class = CardTable

    def get_queryset(self):
        qs = Card.objects.order_by("-pk")
        if not self.request.user.has_perm("kort.view_card"):
            return get_objects_for_user(self.request.user, "kort.view_card", qs)
        return qs


class CardIssueView(PermissionRequiredMixin, RevisionMixin, CookieWizardView):
    """View used to issue one or more cards."""

    permission_required = "kort.create_card_rule"
    context_object_name = "application"
    template_name = "kort/card/issue.html"
    form_list = [CardIssueForm, CardIssueFinishForm]
    success_message = _("The cards have been created successfully.")
    success_url = reverse_lazy("cards")

    def _get_data(self) -> dict[str, any]:
        return self.get_cleaned_data_for_step("0")

    def _get_persons(self) -> QuerySet:
        """Get all persons selected in the first step."""
        return self._get_data()["all_persons"]

    def get_form_initial(self, step: str) -> dict[str, any]:
        if step == "1":
            return {"persons": self._get_persons()}
        return super().get_form_initial(step)

    def get_form_kwargs(self, step: str = None) -> dict[str, any]:
        kwargs = super().get_form_kwargs(step)
        if step == "1":
            kwargs["queryset"] = self._get_persons()
        return kwargs

    def get_form_prefix(self, step: str = None, form: Form = None):
        prefix = super().get_form_prefix(step, form)
        if step == "1":
            return None
        return prefix

    def get_context_data(self, form: Form, **kwargs) -> dict[str, any]:
        context = super().get_context_data(form, **kwargs)
        if self.steps.current == "1":
            table_obj = table_factory(
                Person,
                IssueCardPersonsTable,
                fields=self._get_data()["card_layout"].required_fields,
            )
            table_obj.card_layout = self._get_data()["card_layout"]
            persons_table = table_obj(self._get_persons())
            context["persons_table"] = RequestConfig(self.request, paginate=False).configure(
                persons_table
            )

        return context

    def done(self, form_list: list[Form], **kwargs) -> HttpResponse:
        first_data = form_list[0].cleaned_data
        second_data = form_list[1].cleaned_data

        # Firstly, create all the cards
        cards = []
        for person in second_data["selected_objects"]:
            card = Card(
                person=person,
                layout=first_data["card_layout"],
                valid_until=first_data["valid_until"],
            )
            cards.append(card)
        Card.objects.bulk_create(cards)
        messages.success(self.request, self.success_message)

        # Secondly, print the cards (if activated)
        if first_data.get("printer"):
            printer = first_data["printer"]
            for card in cards:
                try:
                    job = card.print_card(printer)
                    messages.success(
                        self.request,
                        _(
                            "The print job #{} for the card {} on "
                            "the printer {} has been created successfully."
                        ).format(job.pk, card.person, printer.name),
                    )
                except ValueError as e:
                    messages.error(
                        self.request,
                        _(
                            "The print job couldn't be started because of the following error: {}"
                        ).format(e),
                    )
        return redirect(self.success_url)


class CardDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """View used to delete a card."""

    permission_required = "kort.delete_card_rule"
    success_url = reverse_lazy("cards")
    template_name = "kort/card/delete.html"
    model = Card
    success_message = _("The card has been deleted successfully.")


class CardDeactivateView(PermissionRequiredMixin, RevisionMixin, SingleObjectMixin, View):
    """View used to deactivate a card."""

    permission_required = "kort.deactivate_card_rule"
    model = Card
    success_url = reverse_lazy("cards")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.deactivate()
        messages.success(request, _("The card has been deactivated successfully."))
        return redirect(self.success_url)


class CardPrintView(PermissionRequiredMixin, RevisionMixin, SingleObjectMixin, View):
    """View used to create a print job for a card."""

    permission_required = "kort.print_card_rule"
    model = Card
    success_url = reverse_lazy("cards")

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        printer = self.request.GET.get("printer")
        printer = get_object_or_404(CardPrinter, pk=printer)

        try:
            job = self.object.print_card(printer)
            messages.success(
                request,
                _(
                    "The print job #{} for the card {} on "
                    "the printer {} has been created successfully."
                ).format(job.pk, self.object.person, printer.name),
            )
        except ValueError as e:
            messages.error(
                request,
                _("The print job couldn't be started because of the following error: {}").format(e),
            )

        return redirect(self.success_url)


class CardDetailView(PermissionRequiredMixin, RevisionMixin, PrinterSelectMixin, DetailView):
    permission_required = "kort.view_card_rule"
    model = Card
    template_name = "kort/card/detail.html"


class CardGeneratePDFView(PermissionRequiredMixin, RevisionMixin, SingleObjectMixin, View):
    permission_required = "views.edit_card_rule"
    model = Card

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        if not self.object.chip_number:
            messages.error(request, _("The chip number is missing."))
            return redirect("cards")

        redirect_url = reverse("card", args=[self.object.pk])
        result = self.object.generate_pdf()

        if result is True:
            return redirect(redirect_url)

        return render_progress_page(
            request,
            result,
            title=_("Progress: Generate card layout as PDF file"),
            progress_title=_("Generating PDF file …"),
            success_message=_("The PDF file with the card layout has been generated successfully."),
            error_message=_("There was a problem while generating the PDF file."),
            redirect_on_success_url=redirect_url,
            button_title=_("Show card"),
            button_url=redirect_url,
            button_icon="credit_card",
        )


class CardPrinterListView(PermissionRequiredMixin, RevisionMixin, SingleTableView):
    """List view for all card printers."""

    permission_required = "kort.view_cardprinters_rule"
    template_name = "kort/printer/list.html"
    model = CardPrinter
    table_class = CardPrinterTable

    def get_queryset(self):
        qs = CardPrinter.objects.all().annotate(
            jobs_count=Count(
                "jobs", filter=~Q(jobs__status__in=[PrintStatus.FINISHED, PrintStatus.FAILED])
            )
        )

        if not self.request.user.has_perm("kort.view_cardprinter"):
            return get_objects_for_user(self.request.user, "kort.view_cardprinter", CardPrinter)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        CardPrinter.check_online_status_for_all(self.get_queryset())
        return context


class CardPrinterCreateView(PermissionRequiredMixin, RevisionMixin, AdvancedCreateView):
    """View used to create a card printer."""

    permission_required = "kort.create_cardprinter_rule"
    template_name = "kort/printer/create.html"
    form_class = CardPrinterForm
    model = CardPrinter
    success_message = _("The card printer has been created successfully.")

    def get_success_url(self):
        return reverse("card_printer", args=[self.object.pk])


class CardPrinterEditView(PermissionRequiredMixin, RevisionMixin, AdvancedEditView):
    """View used to edit a card printer."""

    permission_required = "kort.edit_cardprinter_rule"
    template_name = "kort/printer/edit.html"
    form_class = CardPrinterForm
    model = CardPrinter
    success_message = _("The card printer has been changed successfully.")

    def get_success_url(self):
        return reverse("card_printer", args=[self.object.pk])


class CardPrinterDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """View used to delete a card printer."""

    permission_required = "kort.delete_cardprinter_rule"
    success_url = reverse_lazy("card_printers")
    template_name = "kort/printer/delete.html"
    model = CardPrinter
    success_message = _("The card printer has been deleted successfully.")


class CardPrinterDetailView(PermissionRequiredMixin, RevisionMixin, DetailView):
    permission_required = "kort.view_cardprinter_rule"
    model = CardPrinter
    template_name = "kort/printer/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.check_online_status()
        return context


class CardLayoutFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = CardLayoutMediaFileFormSet(
            self.request.POST or None, self.request.FILES or None, instance=self.object
        )
        context["formset"] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        form = self.get_form()
        if form.is_valid() and self.formset.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.formset.instance = self.object
        self.formset.save()
        return super().form_valid(form)


class CardLayoutListView(PermissionRequiredMixin, RevisionMixin, SingleTableView):
    """List view for all card layouts."""

    permission_required = "kort.view_cardlayouts_rule"
    template_name = "kort/card_layout/list.html"
    model = CardLayout
    table_class = CardLayoutTable

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.has_perm("kort.view_cardlayout"):
            return get_objects_for_user(self.request.user, "kort.view_cardlayout", CardPrinter)
        return qs


class CardLayoutCreateView(
    PermissionRequiredMixin, CardLayoutFormMixin, RevisionMixin, AdvancedCreateView
):
    """View used to create a card layout."""

    permission_required = "kort.create_cardlayout_rule"
    template_name = "kort/card_layout/create.html"
    form_class = CardLayoutForm
    model = CardLayout
    success_message = _("The card layout has been created successfully.")

    def get_success_url(self):
        return reverse("card_layout", args=[self.object.pk])

    def get_object(self):
        return None


class CardLayoutEditView(
    PermissionRequiredMixin, CardLayoutFormMixin, RevisionMixin, AdvancedEditView
):
    """View used to edit a card layout."""

    permission_required = "kort.edit_cardlayout_rule"
    template_name = "kort/card_layout/edit.html"
    form_class = CardLayoutForm
    model = CardLayout
    success_message = _("The card layout has been changed successfully.")

    def get_success_url(self):
        return reverse("card_layout", args=[self.object.pk])


class CardLayoutDeleteView(PermissionRequiredMixin, RevisionMixin, AdvancedDeleteView):
    """View used to delete a card layout."""

    permission_required = "kort.delete_cardlayout_rule"
    success_url = reverse_lazy("card_layouts")
    template_name = "kort/card_layout/delete.html"
    model = CardLayout
    success_message = _("The card layout has been deleted successfully.")


class CardLayoutDetailView(PermissionRequiredMixin, RevisionMixin, DetailView):
    permission_required = "kort.view_cardlayout_rule"
    model = CardLayout
    template_name = "kort/card_layout/detail.html"


class CardPrinterConfigView(PermissionRequiredMixin, RevisionMixin, SingleObjectMixin, View):
    permission_required = "kort.view_cardprinter_rule"
    model = CardPrinter

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        response = HttpResponse(
            json.dumps(self.object.generate_config()), content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="{self.object.config_filename}"'
        return response
