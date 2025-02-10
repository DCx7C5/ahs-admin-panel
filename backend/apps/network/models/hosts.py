import logging
from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
    Model,
    DateTimeField,
    BooleanField, Q, ManyToManyField, Manager,
)
from django.utils.translation import gettext_lazy as _
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from backend.apps.workspaces.models import Workspace

logger = logging.getLogger(__name__)


class HostManager(Manager):
    """
    Custom manager for the Host model, providing helper methods to handle operations
    related to ManyToMany relationships and other complex querying.
    """

    def create_host(self, hostname=None, ip_addresses=None, is_localhost=False, is_systemhost=False, workspace=None):
        """
        Helper method to create and save a Host instance with optional ManyToMany relationships.
        """
        host = self.model(
            hostname=hostname,
            is_localhost=is_localhost,
            is_systemhost=is_systemhost,
            workspace=workspace,
        )
        host.save()  # Save the Host object to the database before handling ManyToMany fields
        if ip_addresses:
            host.ip_addresses.add(*ip_addresses)  # Add the related IP addresses
        return host

    def get_localhost(self):
        """
        Get the localhost Host object if it exists.
        """
        return self.filter(is_localhost=True).first()

    def get_system_hosts(self):
        """
        Get all hosts marked as system hosts.
        """
        return self.filter(is_systemhost=True)

    def get_hosts_by_workspace(self, workspace):
        """
        Get all hosts associated with a specific workspace.
        """
        return self.filter(workspace=workspace)

    def add_ip_addresses(self, host, ip_addresses):
        """
        Add IP addresses to the specified host.
        """
        if not isinstance(ip_addresses, list):
            ip_addresses = [ip_addresses]
        host.ip_addresses.add(*ip_addresses)

    def remove_ip_addresses(self, host, ip_addresses):
        """
        Remove IP addresses from the specified host.
        """
        if not isinstance(ip_addresses, list):
            ip_addresses = [ip_addresses]
        host.ip_addresses.remove(*ip_addresses)


class Host(Model):
    """
    Represents all types of hosts: localhost, system hosts, and workspace-related regular hosts.
    """

    hostname = CharField(
        max_length=253,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Hostname",
        help_text=_("Optional hostname, must be unique across all host types."),
    )

    ip_addresses = ManyToManyField(
        'IPAddress',
        verbose_name='IP Addresses',
        help_text='External IP addresses associated with this host.',
    )

    is_localhost = BooleanField(
        default=False,
        verbose_name="Is Localhost",
        help_text=_("Unique flag to denote localhost. Only one localhost is allowed."),
    )

    is_systemhost = BooleanField(
        default=False,
        verbose_name="Is System Host",
        help_text=_("Indicates if this is a system host. System hosts must have no workspace."),
    )

    workspace = ForeignKey(
        to=Workspace,
        on_delete=CASCADE,
        related_name="hosts",
        related_query_name="host",
        verbose_name="Workspace",
        null=True,
        blank=True,
        help_text=_("Workspace for regular hosts. Null for localhost and system hosts."),
    )

    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text=_("The timestamp when the host was created.")
    )

    updated_at = DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text=_("The timestamp for the latest update to the host.")
    )

    class Meta:
        app_label = "ahs_core"
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        ordering = ["-created_at"]

        constraints = [
            # There can only be one row where is_localhost is True
            UniqueConstraint(
                fields=["is_localhost"],
                condition=Q(is_localhost=True) | Q(hostname="localhost"),
                name="unique_localhost_constraint",
            ),

            # If is_localhost is True, workspace_id must be NULL
            CheckConstraint(
                check=(
                        Q(is_localhost=True, workspace_id__isnull=True) |
                        Q(is_localhost=False)
                ),
                name="localhost_no_workspace_constraint",
            ),
            # If is_systemhost is True, workspace_id must be NULL
            CheckConstraint(
                check=(
                        Q(is_systemhost=True, workspace_id__isnull=True) |
                        Q(is_systemhost=False)
                ),
                name="systemhost_no_workspace_constraint",
            ),
        ]
