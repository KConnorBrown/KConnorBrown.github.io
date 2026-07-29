from django.db import models


class AboutProfile(models.Model):
    """Singleton profile content for the About Me page."""

    display_name = models.CharField(max_length=120, default="Connor Brown")
    handle = models.CharField(max_length=80, default="@connorbrown", blank=True)
    blurb = models.TextField(
        blank=True,
        default="",
        help_text="Public bio shown on the About Me page.",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About profile"
        verbose_name_plural = "About profile"

    def __str__(self):
        return self.display_name

    @classmethod
    def get_solo(cls):
        obj, _created = cls.objects.get_or_create(pk=1)
        return obj
