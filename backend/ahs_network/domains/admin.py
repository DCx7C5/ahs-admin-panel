from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.ahs_network.domains.models import Domain


@admin.register(Domain)
class DomainAdmin(ModelAdmin):
    list_display = ("id", "domain_name", "host", "is_active", "tld", "registration_date", "expiry_date")
    list_filter = ("is_active", "ssl_enabled", "tld")
    search_fields = ("domain_name", "tld", "registered_by")
    ordering = ("-registration_date",)
