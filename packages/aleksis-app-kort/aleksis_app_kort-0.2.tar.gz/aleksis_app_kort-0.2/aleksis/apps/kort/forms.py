from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _

from django_ace import AceWidget
from django_select2.forms import ModelSelect2MultipleWidget
from material import Fieldset, Layout, Row

from aleksis.apps.kort.models import CardLayout, CardLayoutMediaFile, CardPrinter
from aleksis.core.models import Group, Person


class CardIssueForm(forms.Form):
    layout = Layout(
        Fieldset(_("Select person(s) or group(s)"), "persons", "groups"),
        Fieldset(_("Select validity"), "valid_until"),
        Fieldset(_("Select layout"), "card_layout"),
        Fieldset(_("Select printer (optional)"), "printer"),
    )
    printer = forms.ModelChoiceField(
        queryset=None,
        label=_("Card Printer"),
        help_text=_("Select a printer to directly print the newly issued card."),
        required=False,
    )
    persons = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Persons"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Groups"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    card_layout = forms.ModelChoiceField(queryset=None, label=_("Card layout"), required=True)
    valid_until = forms.DateField(
        label=_("Valid until"),
        required=True,
    )

    def clean(self):
        """Clean and validate person data."""
        cleaned_data = super().clean()

        # Ensure that there is at least one person selected
        if not cleaned_data.get("persons") and not cleaned_data.get("groups"):
            raise forms.ValidationError(_("You must select at least one person or group."))

        cleaned_data["all_persons"] = Person.objects.filter(
            Q(pk__in=cleaned_data.get("persons", []))
            | Q(member_of__in=cleaned_data.get("groups", []))
        ).distinct()

        if not cleaned_data["all_persons"].exists():
            raise forms.ValidationError(_("The selected groups don't have any members."))

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Assume that users would select the layout if there is only one layout available
        layouts = CardLayout.objects.all()
        self.fields["card_layout"].queryset = layouts
        if layouts.count() == 1:
            self.fields["card_layout"].initial = layouts.first()

        self.fields["printer"].queryset = CardPrinter.objects.all()
        self.fields["persons"].queryset = Person.objects.all()
        self.fields["groups"].queryset = Group.objects.all()


class CardPrinterForm(forms.ModelForm):
    layout = Layout(
        Fieldset(_("Generic attributes"), "name", "location", "description"),
        Fieldset(
            _("Printer settings"), "cups_printer", "generate_number_on_server", "card_detector"
        ),
    )

    class Meta:
        model = CardPrinter
        fields = [
            "name",
            "location",
            "description",
            "cups_printer",
            "generate_number_on_server",
            "card_detector",
        ]


class PrinterSelectForm(forms.Form):
    layout = Layout("printer")
    printer = forms.ModelChoiceField(queryset=None, label=_("Card Printer"), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        printers = CardPrinter.objects.all()
        self.fields["printer"].queryset = printers
        if printers.count() == 1:
            self.fields["printer"].initial = printers.first()


class CardLayoutMediaFileForm(forms.ModelForm):
    layout = Layout(Row("media_file", "DELETE"))

    class Meta:
        model = CardLayoutMediaFile
        fields = ["media_file"]


class CardLayoutForm(forms.ModelForm):
    layout = Layout(
        Row("name"), Row("required_fields"), Row("width", "height"), Row("template"), "css"
    )

    template = forms.CharField(widget=AceWidget(mode="django"))
    css = forms.CharField(widget=AceWidget(mode="css"))

    required_fields = forms.MultipleChoiceField(
        label=_("Required data fields"), required=True, choices=Person.syncable_fields_choices()
    )

    class Meta:
        model = CardLayout
        fields = ["name", "template", "css", "width", "height", "required_fields"]


CardLayoutMediaFileFormSet = forms.inlineformset_factory(
    CardLayout, CardLayoutMediaFile, form=CardLayoutMediaFileForm
)


class CardIssueFinishForm(forms.Form):
    layout = Layout()
    selected_objects = forms.ModelMultipleChoiceField(queryset=None, required=True)

    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop("queryset")
        super().__init__(*args, **kwargs)
        self.fields["selected_objects"].queryset = queryset
