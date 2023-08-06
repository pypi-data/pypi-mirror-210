from django.apps import apps
from django.db import models
from django.db.models import functions
from django.utils.translation import gettext as _

from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.kort"
    verbose_name = "AlekSIS — Kort (manage student IDs)"
    dist_name = "AlekSIS-App-Kort"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/onboarding//AlekSIS-App-Kort",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        (
            [2021, 2022],
            "Jonathan Weth",
            "dev@jonathanweth.de",
        ),
        ([2021], "Margarete Grassl", "grasslma@katharineum.de"),
    )

    @classmethod
    def get_all_scopes(cls) -> dict[str, str]:
        """Return all OAuth scopes and their descriptions for this app."""
        CardPrinter = apps.get_model("kort", "CardPrinter")
        label_prefix = _("Access and manage printer status and print jobs")
        scopes = dict(
            CardPrinter.objects.annotate(
                scope=functions.Concat(
                    models.Value(f"{CardPrinter.SCOPE_PREFIX}_"),
                    models.F("id"),
                    output_field=models.CharField(),
                ),
                label=functions.Concat(models.Value(f"{label_prefix}: "), models.F("name")),
            )
            .values_list("scope", "label")
            .distinct()
        )
        return scopes
