from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("journal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="journalentry",
            name="instagram_shortcode",
            field=models.CharField(blank=True, max_length=32, null=True, unique=True),
        ),
    ]
