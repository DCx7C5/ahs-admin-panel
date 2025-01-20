import logging

from django.db.models import (
    CharField,
    GenericIPAddressField,
    Model, DateTimeField,
)

logger = logging.getLogger(__name__)


class SystemHost(Model):

    address = GenericIPAddressField(
        unique=True,
        blank=False,
        protocol='IPv4',
    )

    hostname = CharField(
        max_length=253,
        unique=True,
        blank=True,
    )

    created_at = DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        app_label = 'core'
        verbose_name = "System Host"
        verbose_name_plural = "System Hosts"
        ordering = ["-created_at"]
