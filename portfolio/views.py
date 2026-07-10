from django.shortcuts import get_object_or_404, render

from .models import Project


def project_list(request):
    projects = Project.objects.all()
    return render(
        request,
        "portfolio/project_list.html",
        {
            "title": "Development Portfolio",
            "intro": "Selected software projects and experiments.",
            "projects": projects,
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(
        request,
        "portfolio/project_detail.html",
        {
            "title": project.title,
            "project": project,
        },
    )
