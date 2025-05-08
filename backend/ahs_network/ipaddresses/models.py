from django.db.models import (
    Model,
    GenericIPAddressField,
    DateTimeField, Q, Manager,
)
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from django.utils.translation import gettext_lazy as _


class IPAddressManager(Manager):
    ...


class IPAddress(Model):
    """
    Represents an individual IP address.
    """

    address = GenericIPAddressField(
        protocol='IPv4',
        verbose_name="IP Address",
        help_text=_("Unique IPv4 address (e.g., 192.168.1.1)."),
    )

    created_at = DateTimeField(
        auto_now_add=True,
        help_text=_("The timestamp when the IP address was created."),
    )

    updated_at = DateTimeField(
        auto_now=True,
        help_text=_("The timestamp for the latest update to the IP address."),
    )

    objects = IPAddressManager()

    class Meta:
        app_label = "ahs_network"
        verbose_name = "IP Address"
        verbose_name_plural = "IP Addresses"
        ordering = ["address"]
        db_table = "ahs_network_ip_addresses"

    def __str__(self):
        return self.address
