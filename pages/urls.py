from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("about/blurb/", views.update_about_blurb, name="update_about_blurb"),
]
