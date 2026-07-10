from django.urls import path

from . import views

urlpatterns = [
    path("", views.writing_home, name="writing_home"),
    path("login/", views.WritingLoginView.as_view(), name="writing_login"),
    path("<slug:slug>/", views.post_detail, name="post_detail"),
]
