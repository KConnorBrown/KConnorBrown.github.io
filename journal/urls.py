from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path("photography/", views.photography, name="photography"),
    path(
        "visual-art/",
        RedirectView.as_view(pattern_name="photography", permanent=False),
    ),
    path("gardening-design/", views.gardening_design, name="gardening_design"),
    path("interior-design/", views.interior_design, name="interior_design"),
    path("my-art/", views.my_art, name="my_art"),
    path(
        "interior-design/<slug:slug>/",
        views.design_project_detail,
        name="design_project_detail",
    ),
    path("photo-journal/", views.photo_journal, name="photo_journal"),
    path("photo-journal/curate/", views.curate_photo_journal, name="curate_photo_journal"),
    path(
        "photo-journal/curate/bulk/",
        views.bulk_curate_photos,
        name="bulk_curate_photos",
    ),
    path(
        "photo-journal/<int:pk>/delete/",
        views.delete_journal_entry,
        name="delete_journal_entry",
    ),
    path(
        "photo-journal/<int:pk>/unpublish/",
        views.unpublish_journal_entry,
        name="unpublish_journal_entry",
    ),
    path(
        "photo-journal/<int:pk>/tags/<slug:tag_slug>/remove/",
        views.remove_journal_entry_tag,
        name="remove_journal_entry_tag",
    ),
]
