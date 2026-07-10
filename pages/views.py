from django.shortcuts import render


def home(request):
    return render(
        request,
        "pages/home.html",
        {
            "title": "Connor Brown",
            "intro": "A living portfolio of code, art, words, and spaces.",
        },
    )


def visual_art(request):
    return render(
        request,
        "pages/section.html",
        {
            "title": "Visual Art",
            "intro": "A chronological archive and an interactive viewing experience.",
        },
    )
