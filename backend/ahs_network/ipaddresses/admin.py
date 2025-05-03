from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_network.ipaddresses.models import IPAddress


@admin.register(IPAddress)
class IPAddressAdmin(ModelAdmin):
    ordering = ('id', 'address', 'created_at', 'updated_at')
    list_display = ('id', 'address', 'created_at', 'updated_at')
    search_fields = ('address',)
