import markdown
from django.db import models


class Post(models.Model):
    TYPE_POETRY = "poetry"
    TYPE_CREATIVE_NONFICTION = "creative-nonfiction"
    TYPE_ESSAY = "essay"
    TYPE_CHOICES = [
        (TYPE_POETRY, "Poetry"),
        (TYPE_CREATIVE_NONFICTION, "Creative nonfiction"),
        (TYPE_ESSAY, "Essay"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    post_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_ESSAY)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def rendered_body(self):
        return markdown.markdown(self.body, extensions=["extra", "smarty"])
