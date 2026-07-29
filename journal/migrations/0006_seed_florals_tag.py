from django.db import migrations
from django.utils.text import slugify

TAG_NAMES = ["Florals"]


def seed_tags(apps, schema_editor):
    Tag = apps.get_model("journal", "Tag")
    for name in TAG_NAMES:
        Tag.objects.get_or_create(slug=slugify(name), defaults={"name": name})


def remove_tags(apps, schema_editor):
    Tag = apps.get_model("journal", "Tag")
    Tag.objects.filter(slug__in=[slugify(name) for name in TAG_NAMES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("journal", "0005_seed_tags"),
    ]

    operations = [
        migrations.RunPython(seed_tags, remove_tags),
    ]
