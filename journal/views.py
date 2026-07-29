from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from pages.site_nav import site_nav_context

from .filter_tags import JOURNAL_FILTER_TAGS, filter_tag_by_slug
from .models import DesignProject, JournalEntry, PhotoCollection, Tag

SECTION_TAG_SLUGS = {
    "photography": ["photography"],
    "gardening-design": ["gardening"],
    "interior-design": ["interior-design"],
    "my-art": ["my-art"],
}

SECTION_META = {
    "photography": {
        "title": "Photography",
        "intro": "Photos tagged photography.",
    },
    "gardening-design": {
        "title": "Gardening Design",
        "intro": "Planted spaces, containers, and growing experiments.",
    },
    "interior-design": {
        "title": "Interior Design",
        "intro": "Spaces, objects, and interior studies.",
    },
    "my-art": {
        "title": "My Art",
        "intro": "Art I've made.",
    },
}


def published_entries_for_tags(tag_slugs):
    return (
        JournalEntry.objects.filter(
            is_published=True,
            tags__slug__in=tag_slugs,
        )
        .distinct()
        .prefetch_related("tags")
    )


def _gallery_context(*, section_key, entries, request=None, tags=None, active_tag=None, filter_tag_slugs=None):
    meta = SECTION_META[section_key]
    can_curate = bool(request and request.user.is_staff)
    context = site_nav_context(
        active_key=section_key,
        title=meta["title"],
        intro=meta["intro"],
    )
    context.update(
        {
            "entries": entries,
            "tags": tags or [],
            "active_tag": active_tag,
            "can_curate": can_curate,
            "filter_tag_slugs": filter_tag_slugs or [],
        }
    )
    return context


def photography(request):
    slugs = SECTION_TAG_SLUGS["photography"]
    return render(
        request,
        "journal/gallery.html",
        _gallery_context(
            section_key="photography",
            entries=published_entries_for_tags(slugs),
            request=request,
            filter_tag_slugs=slugs,
        ),
    )


def gardening_design(request):
    slugs = SECTION_TAG_SLUGS["gardening-design"]
    return render(
        request,
        "journal/gallery.html",
        _gallery_context(
            section_key="gardening-design",
            entries=published_entries_for_tags(slugs),
            request=request,
            filter_tag_slugs=slugs,
        ),
    )


def interior_design(request):
    slugs = SECTION_TAG_SLUGS["interior-design"]
    return render(
        request,
        "journal/gallery.html",
        _gallery_context(
            section_key="interior-design",
            entries=published_entries_for_tags(slugs),
            request=request,
            filter_tag_slugs=slugs,
        ),
    )


def my_art(request):
    slugs = SECTION_TAG_SLUGS["my-art"]
    return render(
        request,
        "journal/gallery.html",
        _gallery_context(
            section_key="my-art",
            entries=published_entries_for_tags(slugs),
            request=request,
            filter_tag_slugs=slugs,
        ),
    )


def photo_journal(request):
    tag_slug = request.GET.get("tag", "").strip()
    collection_slug = request.GET.get("collection", "").strip()
    collections = PhotoCollection.objects.filter(is_published=True)
    tags = Tag.objects.all()

    # Load the full published set once; tag filtering happens client-side.
    entries_qs = JournalEntry.objects.prefetch_related("tags", "collections")
    if not request.user.is_staff:
        entries_qs = entries_qs.filter(is_published=True)
    entries = list(entries_qs)

    active_tag = None
    active_collection = None
    active_filter = None

    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        active_filter = filter_tag_by_slug(tag_slug)
        intro = f"Photos tagged {active_tag.name}."
        title = f"Photo Journal · {active_tag.name}"
    elif collection_slug:
        active_collection = get_object_or_404(
            PhotoCollection,
            slug=collection_slug,
            is_published=True,
        )
        entries = [
            entry
            for entry in entries
            if active_collection in entry.collections.all()
        ]
        intro = (
            active_collection.summary
            or "A living grid of moments across places and people."
        )
        title = active_collection.title
    else:
        intro = "All photos — filter by tag to narrow the stream."
        title = "Photo Journal"

    active_slug = active_tag.slug if active_tag else None
    for entry in entries:
        slugs = [tag.slug for tag in entry.tags.all()]
        entry.data_tags = " ".join(slugs)
        entry.filter_hidden = bool(active_slug and active_slug not in slugs)

    context = site_nav_context(
        active_key="photo-journal",
        title=title,
        intro=intro,
    )
    context.update(
        {
            "entries": entries,
            "collections": collections,
            "active_collection": active_collection,
            "tags": tags,
            "active_tag": active_tag,
            "active_filter": active_filter,
            "journal_filter_tags": JOURNAL_FILTER_TAGS,
            "can_curate": request.user.is_staff,
            "filter_tag_slugs": [active_tag.slug] if active_tag else [],
        }
    )
    return render(request, "journal/photo_journal.html", context)


@staff_member_required
def curate_photo_journal(request):
    status = request.GET.get("status", "published").strip()
    tag_slug = request.GET.get("tag", "").strip()
    entries = JournalEntry.objects.prefetch_related("tags").all()

    if status == "hidden":
        entries = entries.filter(is_published=False)
    elif status == "untagged":
        entries = entries.filter(tags__isnull=True)
        status = "untagged"
    elif status == "all":
        pass
    else:
        status = "published"
        entries = entries.filter(is_published=True)

    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        entries = entries.filter(tags=active_tag).distinct()

    return render(
        request,
        "journal/curate.html",
        {
            "title": "Curate Photo Journal",
            "intro": (
                "Select photos to tag, hide, or delete in bulk. "
                "Hidden photos stay on disk; deleted photos are removed."
            ),
            "entries": entries,
            "status": status,
            "tags": Tag.objects.all(),
            "active_tag": active_tag,
            "counts": {
                "all": JournalEntry.objects.count(),
                "published": JournalEntry.objects.filter(is_published=True).count(),
                "hidden": JournalEntry.objects.filter(is_published=False).count(),
                "untagged": JournalEntry.objects.filter(tags__isnull=True).count(),
            },
        },
    )


@staff_member_required
@require_POST
def bulk_curate_photos(request):
    action = request.POST.get("action", "").strip()
    raw_ids = request.POST.getlist("entry_ids")
    try:
        entry_ids = [int(value) for value in raw_ids]
    except ValueError:
        messages.error(request, "Invalid photo selection.")
        return redirect("curate_photo_journal")

    queryset = JournalEntry.objects.filter(pk__in=entry_ids)
    selected = queryset.count()

    if selected == 0:
        messages.warning(request, "No photos selected.")
        return redirect("curate_photo_journal")

    next_url = request.POST.get("next") or "/photo-journal/curate/"

    if action in {"add_tags", "remove_tags"}:
        tag_ids = request.POST.getlist("tag_ids")
        selected_tags = list(Tag.objects.filter(pk__in=tag_ids))
        if not selected_tags:
            messages.warning(request, "No tags selected.")
            return redirect(next_url if next_url.startswith("/") else "curate_photo_journal")

        label = ", ".join(tag.name for tag in selected_tags)
        if action == "add_tags":
            for entry in queryset:
                entry.tags.add(*selected_tags)
            messages.success(request, f"Added [{label}] to {selected} photo(s).")
        else:
            for entry in queryset:
                entry.tags.remove(*selected_tags)
            messages.success(request, f"Removed [{label}] from {selected} photo(s).")
    elif action == "hide":
        updated = queryset.update(is_published=False)
        messages.success(request, f"Hid {updated} photo(s) from the public grid.")
    elif action == "publish":
        updated = queryset.update(is_published=True)
        messages.success(request, f"Published {updated} photo(s).")
    elif action == "delete":
        deleted = 0
        for entry in queryset:
            entry.delete()
            deleted += 1
        messages.success(request, f"Deleted {deleted} photo(s) permanently.")
    else:
        messages.error(request, "Unknown curation action.")

    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("curate_photo_journal")


@staff_member_required
@require_POST
def delete_journal_entry(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    entry.delete()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True})

    next_url = request.POST.get("next") or "photo_journal"
    if next_url.startswith("/"):
        return redirect(next_url)
    return redirect("photo_journal")


@staff_member_required
@require_POST
def unpublish_journal_entry(request, pk):
    entry = get_object_or_404(JournalEntry, pk=pk)
    entry.is_published = False
    entry.save(update_fields=["is_published"])

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "is_published": False})
    return redirect("photo_journal")


@staff_member_required
@require_POST
def remove_journal_entry_tag(request, pk, tag_slug):
    entry = get_object_or_404(JournalEntry, pk=pk)
    tag = get_object_or_404(Tag, slug=tag_slug)
    entry.tags.remove(tag)
    remaining = list(entry.tags.values("slug", "name"))

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "tags": remaining})
    return redirect("photo_journal")


def design_project_detail(request, slug):
    project = get_object_or_404(DesignProject, slug=slug)
    return render(
        request,
        "journal/design_project_detail.html",
        {
            "title": project.title,
            "project": project,
        },
    )
