from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from pages.site_nav import site_nav_context

from .models import AboutProfile


def home(request):
    context = site_nav_context(
        active_key=None,
        title="Connor Brown",
        intro="Code, images, words, and spaces.",
    )
    context["entries"] = []
    context["can_curate"] = False
    context["filter_tag_slugs"] = []
    return render(request, "pages/home.html", context)


def about(request):
    profile = AboutProfile.get_solo()
    context = site_nav_context(
        active_key="about",
        title="About Me",
        intro=profile.blurb or "A bit about Connor.",
    )
    context.update(
        {
            "entries": [],
            "can_curate": False,
            "filter_tag_slugs": [],
            "profile": profile,
            "can_edit_about": request.user.is_staff,
        }
    )
    return render(request, "pages/about.html", context)


@staff_member_required
@require_POST
def update_about_blurb(request):
    profile = AboutProfile.get_solo()
    profile.blurb = request.POST.get("blurb", "").strip()
    display_name = request.POST.get("display_name", "").strip()
    handle = request.POST.get("handle", "").strip()
    if display_name:
        profile.display_name = display_name
    if "handle" in request.POST:
        profile.handle = handle
    profile.save()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {
                "ok": True,
                "blurb": profile.blurb,
                "display_name": profile.display_name,
                "handle": profile.handle,
            }
        )
    return redirect("about")
