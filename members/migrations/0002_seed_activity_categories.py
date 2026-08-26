from django.db import migrations

INITIAL_CATEGORIES = [
    "Crew Meeting",
    "Skill",
    "Campus Program",
    "Logbook",
    "Training",
    "Community Service",
    "Event Participation",
    "Leadership",
    "Other",
]


def seed_categories(apps, schema_editor):
    ActivityCategory = apps.get_model("members", "ActivityCategory")
    for name in INITIAL_CATEGORIES:
        ActivityCategory.objects.get_or_create(name=name)


def unseed_categories(apps, schema_editor):
    ActivityCategory = apps.get_model("members", "ActivityCategory")
    ActivityCategory.objects.filter(name__in=INITIAL_CATEGORIES).delete()


class Migration(migrations.Migration):
    dependencies = [("members", "0001_initial")]
    operations = [migrations.RunPython(seed_categories, unseed_categories)]
