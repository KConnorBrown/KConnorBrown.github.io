from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from pages.site_nav import site_nav_context

from .models import Post


def writing_home(request):
    context = site_nav_context(
        active_key="writing",
        title="Writing",
        intro="Essays, notes, and drafts in progress.",
    )
    context.update(
        {
            "entries": [],
            "can_curate": False,
            "filter_tag_slugs": [],
        }
    )

    if not request.user.is_authenticated:
        return render(request, "writing/login_prompt.html", context)

    context["posts"] = Post.objects.filter(status=Post.STATUS_PUBLISHED)
    return render(request, "writing/post_list.html", context)


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.STATUS_PUBLISHED)
    context = site_nav_context(
        active_key="writing",
        title=post.title,
        intro=post.get_post_type_display(),
    )
    context.update(
        {
            "entries": [],
            "can_curate": False,
            "filter_tag_slugs": [],
            "post": post,
        }
    )
    return render(request, "writing/post_detail.html", context)


class WritingLoginView(auth_views.LoginView):
    template_name = "writing/login.html"
