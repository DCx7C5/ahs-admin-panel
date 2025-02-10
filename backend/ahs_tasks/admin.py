from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_tasks.models import Task


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ("id", "name", "status", "host", "worker", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "status", "host__hostname")
    ordering = ("-created_at",)
