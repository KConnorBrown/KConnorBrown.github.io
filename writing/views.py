from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Post


def writing_home(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "writing/login_prompt.html",
            {
                "title": "Writing",
                "intro": "Essays, notes, and drafts in progress.",
            },
        )

    posts = Post.objects.filter(status=Post.STATUS_PUBLISHED)
    return render(
        request,
        "writing/post_list.html",
        {
            "title": "Writing",
            "intro": "Essays, notes, and drafts in progress.",
            "posts": posts,
        },
    )


@login_required
def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.STATUS_PUBLISHED)
    return render(
        request,
        "writing/post_detail.html",
        {
            "title": post.title,
            "post": post,
        },
    )


class WritingLoginView(auth_views.LoginView):
    template_name = "writing/login.html"
