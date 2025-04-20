from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.sessions.models import Session

from backend.ahs_core.models import AHSSession
from backend.ahs_core.models.apps import App


@admin.register(App)
class AppModelAdmin(ModelAdmin):
    list_display = ("id", "name", "content_type",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ['session_key', 'session_data', 'expire_date']


@admin.register(AHSSession)
class AHSSessionAdmin(ModelAdmin):
    list_display = ['session_key', 'expire_date']


@admin.register(LogEntry)
class AdminLogAdmin(ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'change_message', 'is_addition', 'is_change', 'is_deletion')
    list_filter = ['action_time', 'user', 'content_type']
    ordering = ('-action_time',)


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ('id', 'name', 'content_type', 'codename')
    ordering = ('id',)


admin.site.unregister(Group)
