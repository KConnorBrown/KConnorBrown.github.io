from django.db import models


class JournalEntry(models.Model):
    TAG_INTERIOR_DESIGN = "interior-design"
    TAG_GARDENING = "gardening"
    TAG_SMALL_SPACES = "small-spaces"
    TAG_CURATION = "curation"
    TAG_CHOICES = [
        (TAG_INTERIOR_DESIGN, "Interior design"),
        (TAG_GARDENING, "Gardening"),
        (TAG_SMALL_SPACES, "Small spaces"),
        (TAG_CURATION, "Curation"),
    ]

    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)
    photo = models.ImageField(upload_to="journal/")
    entry_date = models.DateField()
    tag = models.CharField(max_length=30, choices=TAG_CHOICES, default=TAG_CURATION)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        verbose_name_plural = "journal entries"

    def __str__(self):
        return self.title


class DesignProject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField()
    featured_image = models.ImageField(upload_to="design/", blank=True)
    body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
