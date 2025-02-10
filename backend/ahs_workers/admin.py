from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_workers.models import Worker


@admin.register(Worker)
class WorkerAdmin(ModelAdmin):
    list_display = ("id", "name", "status", "last_active_time", "host")
    list_filter = ("status",)
    search_fields = ("name", "api_key")
    ordering = ("-last_active_time",)
