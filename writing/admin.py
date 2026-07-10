from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "post_type", "status", "is_private", "created_at")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("post_type", "status", "is_private")
