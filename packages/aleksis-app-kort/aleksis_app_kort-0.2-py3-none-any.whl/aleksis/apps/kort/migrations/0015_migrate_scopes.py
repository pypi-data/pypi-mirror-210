from django.db import migrations

def _migrate_scopes(apps, schema_editor):
    CardPrinter = apps.get_model("kort", "CardPrinter")
    for printer in CardPrinter.objects.all():
        application = printer.oauth2_application
        application.allowed_scopes = [f"card_printer_{printer.id}"]
        application.authorization_grant_type = "client-credentials"
        application.save()

class Migration(migrations.Migration):

    dependencies = [
        ('kort', '0014_auto_20220803_0025'),
    ]

    operations = [
        migrations.RunPython(_migrate_scopes)
    ]
