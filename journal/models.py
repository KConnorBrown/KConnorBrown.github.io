from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    title = models.CharField(max_length=200)
    caption = models.TextField(blank=True)
    photo = models.ImageField(upload_to="journal/")
    thumbnail = models.ImageField(
        upload_to="journal/thumbs/",
        blank=True,
        help_text="Small grid preview; auto-generated from photo when missing.",
    )
    entry_date = models.DateField()
    tags = models.ManyToManyField(Tag, related_name="entries", blank=True)
    instagram_shortcode = models.CharField(max_length=32, blank=True, null=True, unique=True)
    is_published = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from public grids without deleting.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        verbose_name_plural = "journal entries"

    def __str__(self):
        return self.title

    @property
    def grid_image_url(self) -> str:
        if self.thumbnail:
            return self.thumbnail.url
        if self.photo:
            return self.photo.url
        return ""

    def delete(self, using=None, keep_parents=False):
        storage = self.photo.storage
        photo_path = self.photo.name if self.photo else ""
        thumb_path = self.thumbnail.name if self.thumbnail else ""
        super().delete(using=using, keep_parents=keep_parents)
        if photo_path:
            storage.delete(photo_path)
        if thumb_path:
            storage.delete(thumb_path)


class PhotoCollection(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    summary = models.TextField(blank=True)
    entries = models.ManyToManyField(
        JournalEntry,
        related_name="collections",
        blank=True,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "title"]

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
