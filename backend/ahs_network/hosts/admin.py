from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_network.hosts.models import Host


@admin.register(Host)
class HostAdmin(ModelAdmin):
    list_display = ('id', 'hostname', 'is_localhost', 'is_systemhost', 'created_at', 'updated_at', 'workspace')
    search_fields = ('hostname',)
    ordering = ('id',)
    list_filter = ('is_systemhost', 'is_localhost')
