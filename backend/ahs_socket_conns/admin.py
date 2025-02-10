from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_socket_conns.models import SocketConnection


@admin.register(SocketConnection)
class SocketConnectionAdmin(ModelAdmin):
    list_display = ("id", "url", "status", "lhost", "lport", "user", "connected_at", "rhost", "rport")
    list_filter = ("status", "connected_at")
    search_fields = ("url", "lhost__hostname", "rhost__hostname")
    ordering = ("-connected_at",)
