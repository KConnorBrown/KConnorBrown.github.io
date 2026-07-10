from django.urls import path

from . import views

urlpatterns = [
    path("photo-journal/", views.photo_journal, name="photo_journal"),
    path("interior-design/", views.interior_design, name="interior_design"),
    path(
        "interior-design/<slug:slug>/",
        views.design_project_detail,
        name="design_project_detail",
    ),
]
