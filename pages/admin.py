from django.contrib import admin

from .models import AboutProfile


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "handle", "updated_at")
    fields = ("display_name", "handle", "blurb")
