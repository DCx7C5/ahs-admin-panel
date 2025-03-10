from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_network.hosts.models import Host


@admin.register(Host)
class HostAdmin(ModelAdmin):
    ordering = ('id',)
