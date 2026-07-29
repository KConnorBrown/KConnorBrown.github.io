from django.contrib import admin, messages
from django.shortcuts import render
from django.utils.html import format_html

from .models import DesignProject, JournalEntry, PhotoCollection, Tag


@admin.action(description="Hide selected photos from public site")
def hide_selected_photos(modeladmin, request, queryset):
    queryset.update(is_published=False)


@admin.action(description="Publish selected photos")
def publish_selected_photos(modeladmin, request, queryset):
    queryset.update(is_published=True)


@admin.action(description="Delete selected photos (and media files)")
def delete_selected_photos(modeladmin, request, queryset):
    for entry in queryset:
        entry.delete()


def _batch_tag_response(modeladmin, request, queryset, mode):
    """Shared intermediate page for add/remove tags."""
    tags = Tag.objects.all()
    action_name = "add_tags_to_selected" if mode == "add" else "remove_tags_from_selected"

    if request.POST.get("confirm_batch_tag"):
        tag_ids = request.POST.getlist("tag_ids")
        selected_tags = list(Tag.objects.filter(pk__in=tag_ids))
        if not selected_tags:
            modeladmin.message_user(
                request,
                "No tags selected.",
                level=messages.WARNING,
            )
            return None

        count = queryset.count()
        if mode == "add":
            for entry in queryset:
                entry.tags.add(*selected_tags)
            label = ", ".join(t.name for t in selected_tags)
            modeladmin.message_user(
                request,
                f"Added tag(s) [{label}] to {count} photo(s).",
            )
        else:
            for entry in queryset:
                entry.tags.remove(*selected_tags)
            label = ", ".join(t.name for t in selected_tags)
            modeladmin.message_user(
                request,
                f"Removed tag(s) [{label}] from {count} photo(s).",
            )
        return None

    context = {
        **modeladmin.admin_site.each_context(request),
        "title": "Add tags" if mode == "add" else "Remove tags",
        "opts": modeladmin.model._meta,
        "queryset": queryset,
        "tags": tags,
        "mode": mode,
        "action_name": action_name,
        "media": modeladmin.media,
    }
    return render(request, "admin/journal/batch_tag.html", context)


@admin.action(description="Add tags to selected photos")
def add_tags_to_selected(modeladmin, request, queryset):
    return _batch_tag_response(modeladmin, request, queryset, mode="add")


@admin.action(description="Remove tags from selected photos")
def remove_tags_from_selected(modeladmin, request, queryset):
    return _batch_tag_response(modeladmin, request, queryset, mode="remove")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "tag_list", "entry_date", "is_published")
    list_display_links = ("thumbnail", "title")
    list_filter = ("tags", "is_published", "collections")
    search_fields = ("title", "caption", "instagram_shortcode")
    filter_horizontal = ("tags",)
    actions = (
        add_tags_to_selected,
        remove_tags_from_selected,
        hide_selected_photos,
        publish_selected_photos,
        delete_selected_photos,
    )
    # Show the full import set on one page for large batch tagging.
    list_per_page = 700
    list_max_show_all = 1000
    date_hierarchy = "entry_date"
    readonly_fields = ("photo_preview", "instagram_shortcode", "created_at")
    fields = (
        "photo_preview",
        "photo",
        "title",
        "caption",
        "entry_date",
        "tags",
        "is_published",
        "instagram_shortcode",
        "created_at",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags")

    @admin.display(description="Photo")
    def thumbnail(self, obj):
        if not obj.photo:
            return "—"
        return format_html(
            '<img src="{}" alt="" style="width:72px;height:72px;object-fit:cover;border-radius:8px;" />',
            obj.photo.url,
        )

    @admin.display(description="Preview")
    def photo_preview(self, obj):
        if not obj.photo:
            return "No photo uploaded."
        return format_html(
            '<img src="{}" alt="" style="max-width:520px;max-height:520px;height:auto;'
            'border-radius:12px;border:1px solid #ddd;" />',
            obj.photo.url,
        )

    @admin.display(description="Tags")
    def tag_list(self, obj):
        names = list(obj.tags.values_list("name", flat=True))
        return ", ".join(names) if names else "—"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "entry_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    @admin.display(description="Photos")
    def entry_count(self, obj):
        return obj.entries.count()


@admin.register(PhotoCollection)
class PhotoCollectionAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_published", "created_at")
    list_editable = ("sort_order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("entries",)


@admin.register(DesignProject)
class DesignProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    prepopulated_fields = {"slug": ("title",)}
