from django.db.models.fields.files import ImageFieldFile
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext as _

from django_tables2 import (
    BooleanColumn,
    Column,
    DateTimeColumn,
    LinkColumn,
    RelatedLinkColumn,
    Table,
)
from django_tables2.utils import A, AttributeDict, computed_values

from aleksis.apps.kort.forms import PrinterSelectForm
from aleksis.core.models import Person
from aleksis.core.util.tables import SelectColumn


class CardTable(Table):
    """Table to list cards."""

    class Meta:
        attrs = {"class": "highlight"}

    person = RelatedLinkColumn()
    chip_number = LinkColumn("card", verbose_name=_("Chip number"), args=[A("pk")])
    current_status = Column(verbose_name=_("Current status"), accessor=A("pk"))
    valid_until = Column(verbose_name=_("Valid until"))
    deactivated = BooleanColumn(verbose_name=_("Deactivated"))
    actions = Column(verbose_name=_("Actions"), accessor=A("pk"))

    def render_current_status(self, value, record):
        return render_to_string(
            "kort/card/status.html",
            dict(
                card=record,
            ),
        )

    def render_actions(self, value, record):
        return render_to_string(
            "kort/card/actions.html", dict(pk=value, card=record, printer_form=PrinterSelectForm())
        )


class CardPrinterTable(Table):
    """Table to list card printers."""

    class Meta:
        attrs = {"class": "highlight"}

    name = LinkColumn("card_printer", verbose_name=_("Printer name"), args=[A("pk")])
    location = Column(verbose_name=_("Printer location"))

    current_status = Column(verbose_name=_("Current status"), accessor=A("pk"))
    last_seen_at = DateTimeColumn(verbose_name=_("Last seen at"))
    jobs_count = Column(verbose_name=_("Running jobs"))

    actions = Column(verbose_name=_("Actions"), accessor=A("pk"))

    def render_current_status(self, value, record):
        return render_to_string(
            "kort/printer/status.html",
            dict(
                printer=record,
            ),
        )

    def render_actions(self, value, record):
        return render_to_string("kort/printer/actions.html", dict(pk=value, printer=record))


class CardLayoutTable(Table):
    """Table to list card layouts."""

    class Meta:
        attrs = {"class": "highlight"}

    name = LinkColumn("card_layout", verbose_name=_("Layout name"), args=[A("pk")])
    width = Column()
    height = Column()

    actions = Column(verbose_name=_("Actions"), accessor=A("pk"))

    def render_actions(self, value, record):
        return render_to_string("kort/card_layout/actions.html", dict(pk=value, card_layout=record))


class IssueCardPersonsTable(Table):
    """Table to list persons with all needed data for issueing cards."""

    selected = SelectColumn()
    status = Column(accessor=A("pk"), verbose_name=_("Status"))

    def get_missing_fields(self, person: Person):
        """Return a list of missing data fields for the given person."""
        required_fields = self.card_layout.required_fields
        missing_fields = []
        for field in required_fields:
            if not getattr(person, field, None):
                missing_fields.append(field)
        return missing_fields

    def render_selected(self, value: int, record: Person) -> SafeString:
        """Render the selected checkbox and mark valid rows as selected."""
        attrs = {"type": "checkbox", "name": "selected_objects", "value": value}
        if not self.get_missing_fields(record):
            attrs.update({"checked": "checked"})

        attrs = computed_values(attrs, kwargs={"record": record, "value": value})
        return mark_safe(  # noqa
            "<label><input %s/><span></span</label>" % AttributeDict(attrs).as_html()
        )

    def render_status(self, value: int, record: Person) -> str:
        """Render the status of the person data."""
        missing_fields = self.get_missing_fields(record)
        return render_to_string(
            "kort/person_status.html",
            {"missing_fields": missing_fields, "missing_fields_count": len(missing_fields)},
            self.request,
        )

    def render_photo(self, value: ImageFieldFile, record: Person) -> str:
        """Render the photo of the person as circle."""
        return render_to_string(
            "kort/picture.html",
            {
                "picture": record.photo,
                "class": "materialize-circle table-circle",
                "img_class": "materialize-circle",
            },
            self.request,
        )

    def render_avatar(self, value: ImageFieldFile, record: Person) -> str:
        """Render the avatar of the person as circle."""
        return render_to_string(
            "kort/picture.html",
            {
                "picture": record.avatar,
                "class": "materialize-circle table-circle",
                "img_class": "materialize-circle",
            },
            self.request,
        )

    class Meta:
        sequence = ["selected", "status", "..."]
