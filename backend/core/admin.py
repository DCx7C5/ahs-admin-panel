from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, Permission
from django.contrib.sessions.models import Session

from backend.core.models.host import Host


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ['session_key', 'session_data', 'expire_date']


@admin.register(LogEntry)
class AdminLogAdmin(ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'change_message', 'is_addition', 'is_change', 'is_deletion')
    list_filter = ['action_time', 'user', 'content_type']
    ordering = ('-action_time',)



@admin.register(Host)
class HostAdmin(ModelAdmin):
    ordering = ('id',)
    search_fields = ('name', 'address',)


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ('id', 'name', 'content_type', 'codename')
    ordering = ('id',)


admin.site.unregister(Group)
