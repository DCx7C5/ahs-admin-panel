from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.sessions.models import Session

from backend.ahs_core.models import AHSSession
from backend.ahs_core.models.apps import App

User = get_user_model()

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


@admin.register(User)
class AHSUserAdmin(UserAdmin):
    model = User
    fieldsets = tuple(tuple(
        (section[0], {"fields": tuple(field if field != "email" else "public_key" for field in section[1]["fields"])})
        for
        section in UserAdmin.fieldsets))

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image',)}),
    )
    list_display = tuple(field if field != "email" else "public_key" for field in UserAdmin.list_display)
    search_fields = tuple(field if field != "email" else "public_key" for field in UserAdmin.search_fields)
    show_full_result_count = True



admin.site.unregister(Group)
