from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_network.ipaddresses.models import IPAddress


@admin.register(IPAddress)
class HostAdmin(ModelAdmin):
    ordering = ('id',)
