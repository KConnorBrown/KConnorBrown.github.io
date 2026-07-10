from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("visual-art/", views.visual_art, name="visual_art"),
]
