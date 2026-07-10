from django.shortcuts import get_object_or_404, render

from .models import DesignProject, JournalEntry


def photo_journal(request):
    entries = JournalEntry.objects.all()
    return render(
        request,
        "journal/photo_journal.html",
        {
            "title": "Photo Journal",
            "intro": "A grid-based journal for photographs and moments.",
            "entries": entries,
        },
    )


def interior_design(request):
    entries = JournalEntry.objects.filter(tag=JournalEntry.TAG_INTERIOR_DESIGN)
    projects = DesignProject.objects.all()
    return render(
        request,
        "journal/interior_design.html",
        {
            "title": "Interior Design",
            "intro": "Spaces, studies, and design explorations.",
            "entries": entries,
            "projects": projects,
        },
    )


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
