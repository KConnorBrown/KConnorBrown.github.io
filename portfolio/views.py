from django.shortcuts import get_object_or_404, render

from pages.site_nav import site_nav_context

from .models import Project


def project_list(request):
    context = site_nav_context(
        active_key="development",
        title="Software Development",
        intro="Software projects and experiments.",
    )
    context.update(
        {
            "entries": [],
            "can_curate": False,
            "filter_tag_slugs": [],
            "projects": Project.objects.exclude(slug="sql-playground"),
        }
    )
    return render(request, "portfolio/project_list.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    context = site_nav_context(
        active_key="development",
        title=project.title,
        intro=project.summary,
    )
    context.update(
        {
            "entries": [],
            "can_curate": False,
            "filter_tag_slugs": [],
            "project": project,
        }
    )
    return render(request, "portfolio/project_detail.html", context)
