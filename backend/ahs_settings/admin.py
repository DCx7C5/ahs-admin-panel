from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_settings.models import Settings


@admin.register(Settings)
class AHSSettingsAdmin(ModelAdmin):
    list_display = ("id", "key", "module", "type", "is_active", "updated_at")
    list_filter = ("type", "module", "is_active")
    search_fields = ("key", "value", "module")
    ordering = ("key",)
