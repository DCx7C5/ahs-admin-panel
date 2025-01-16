from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.xapi.models import UserProfile


# Register your models here.

@admin.register(UserProfile)
class XUserProfileAdmin(ModelAdmin):
    list_display = ('username', 'name', 'id')
    ordering = ('id',)
    search_fields = ('name',)
