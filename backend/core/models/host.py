import logging
from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
    Model,
    DateTimeField,
    BooleanField, Q, ManyToManyField,
)
from django.utils.translation import gettext_lazy as _
from django.db.models.constraints import UniqueConstraint, CheckConstraint

from backend.core.models.ipadress import IPAddress
from backend.core.models.workspace import Workspace

logger = logging.getLogger(__name__)




class Host(Model):
    """
    Represents all types of hosts in the system: localhost, system host(s), and workspace-related regular hosts.

    - Localhost: There can only be one localhost, set with `is_localhost=True` and no workspace.
    - System Hosts: A small group of hosts with `is_systemhost=True`, also without a workspace.
    - Regular Hosts: All other hosts, each associated with a workspace.

    Constraints and validations are enforced to ensure proper relations and uniqueness.
    """

    address = ManyToManyField(
        to=IPAddress,
        related_name="hosts",
        verbose_name="IP Addresses",
        help_text=_("List of IP addresses associated with this host."),
    )

    hostname = CharField(
        max_length=253,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Hostname",
        help_text=_("Optional hostname, must be unique across all host types."),
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
        app_label = "core"
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        ordering = ["-created_at"]

        #: Enforces constraints on different host types.
        constraints = [
            # Systemhosts only one IP
            CheckConstraint(
                check=~Q(hosts__is_systemhost=True) | Q(hosts__count__lte=1),
                name="single_ip_per_systemhost_constraint",
            ),
            # Only one localhost allowed
            UniqueConstraint(
                fields=["is_localhost"],
                condition=Q(is_localhost=True),
                name="unique_localhost_constraint",
            ),
            # Hostname constraint for localhost
            UniqueConstraint(
                fields=["hostname"],
                condition=Q(hostname="localhost"),
                name="unique_hostname_localhost_constraint",
            ),
            # Regular hosts must have a workspace
            UniqueConstraint(
                fields=["workspace"],
                condition=Q(is_localhost=False, is_systemhost=False),
                name="regular_host_workspace_constraint",
            ),
            # System hosts must have no workspace
            UniqueConstraint(
                fields=["is_systemhost", "workspace"],
                condition=Q(is_systemhost=True, workspace=None),
                name="system_host_no_workspace_constraint",
            ),
        ]
        permissions = [

        ]

    async def save(self, *args, **kwargs):
        """
        Save the host instance, enforcing constraints for localhost, system hosts, and regular hosts.

        Raises:
            ValueError: If localhost or system host uniqueness conditions are violated,
                        or if regular hosts do not have a workspace.
        """
        if self.is_localhost:
            # Ensure only one localhost exists
            if Host.objects.filter(is_localhost=True).exclude(pk=self.pk).exists():
                raise ValueError("Only one localhost instance is allowed.")
            # Ensure localhost has no workspace
            if self.workspace is not None:
                raise ValueError("Localhost must not be associated with a workspace.")

        if self.is_systemhost:
            # Ensure system host has no workspace
            if self.workspace is not None:
                raise ValueError("System hosts must not be associated with a workspace.")

        elif not self.workspace:
            # Regular hosts must have a workspace
            raise ValueError("Regular hosts must be associated with a workspace.")

        # Only save if validations pass
        super().save(*args, **kwargs)

    def __str__(self):
        """
        String representation of the host.

        Returns:
            str: A string distinguishing between localhost, system hosts, and regular hosts,
                 including their address, hostname, and workspace if applicable.
        """
        if self.is_localhost:
            return f"Localhost ({self.hostname or self.address})"
        if self.is_systemhost:
            return f"System Host ({self.hostname or self.address})"
        return f"Host ({self.hostname or self.address}) in Workspace {self.workspace}"