from django.contrib.auth import get_user_model
from django.db.models import (
    SmallIntegerField,
    DateTimeField,
    ForeignKey,
    CharField,
    CASCADE,
    Model,
    Q,
)
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models.indexes import Index
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from backend.core.models import Host

AHSUser = get_user_model()


class SocketConnection(Model):
    """
    Represents a persistent socket connection between a user and one or more hosts.

    This model stores relevant information about a socket connection, such as the
    local host, remote host, ports, user, status, and timestamps. It is designed
    to track the lifecycle of a connection, including its status and other key
    attributes in a structured manner.

    Attributes:
        url (str): The URL of the socket connection, typically referencing the endpoint
                   of the connection.
        status (str): The current state of the socket connection, with predefined
                      choices including 'connected', 'disconnected', and so on.
        lhost (ForeignKey): Refers to the local host associated with this connection.
                            (see `Host` model). Typically, represents the server machine or
                            system initiating the connection.
                            **Help Text**: "The local host that establishes the connection."
        lport (int): Stores the local port associated with the connection on the local host.
                     The value should remain between 0 and 65535.
        user (ForeignKey): User connected to the socket, represented by a foreign key to
                           the `AHSUser` model.
        connected_at (datetime): Timestamp of when the connection was established.
                                 Automatically set upon creation.
        rhost (ForeignKey): Refers to the remote host associated with this connection.
                            (see `Host` model). Typically, the target machine or system
                            being communicated with.
                            **Help Text**: "The remote host that the local host communicates with."
        rport (int): Stores the remote port associated with the connection on the remote host.
                     The value should remain between 0 and 65535.
        last_updated (datetime): Represents the timestamp of the last update to the
                                 connection details (e.g., status changes).
    """

    SOCKET_STATUS_CHOICES = (
        ('listening', 'Listening'),
        ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('error', 'Error'),
        ('disconnecting', 'Disconnecting'),
        ('disconnected', 'Disconnected'),
        ('idle', 'Idle'),
    )

    url = CharField(
        max_length=255,
        editable=False,
        verbose_name="Socket URL",
        help_text=_("The URL of the socket connection."),
        db_index=True,
    )

    status = CharField(
        max_length=20,
        choices=SOCKET_STATUS_CHOICES,
        default='disconnected',
        verbose_name="Socket Status",
        help_text=_("The current status of the socket connection."),
        db_index=True,
    )

    lhost = ForeignKey(
        Host,
        on_delete=CASCADE,
        related_name="lhost_connections",
        db_index=True,
        help_text=_("The local host that establishes the connection."),
    )

    lport = SmallIntegerField(
        null=False,
        blank=False,
        help_text=_("The port associated with the local host. Must be within the range 0–65535."),
    )

    user = ForeignKey(
        AHSUser,
        on_delete=CASCADE,
        related_name='active_connections',
        related_query_name='active_connection',
        verbose_name="Socket User",
        help_text=_("The user who is connected to the socket.")
    )

    connected_at = DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name="Connected At",
        help_text=_("Timestamp when the connection was established."),
    )

    rhost = ForeignKey(
        Host,
        on_delete=CASCADE,
        related_name="rhost_connections",
        db_index=True,
        help_text=_("The remote host that the local host communicates with."),
    )

    rport = SmallIntegerField(
        null=False,
        blank=False,
        editable=False,
        help_text=_("The port associated with the remote host. Must be within the range 0–65535."),
    )

    last_updated = DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name="Last Updated At",
        help_text=_("Timestamp when the last update was updated."),
    )

    class Meta:
        verbose_name = "Socket Connection"
        verbose_name_plural = "Socket Connections"
        ordering = ['-connected_at']

        constraints = [
            UniqueConstraint(fields=['lhost', 'lport'], name='unique_lhost_lport'),
            UniqueConstraint(fields=['rhost', 'rport'], name='unique_rhost_rport'),
            CheckConstraint(
                check=Q(lport__gte=0, lport__lte=65535),
                name="check_valid_lport_range",
            ),
            CheckConstraint(
                check=Q(rport__gte=0, rport__lte=65535),
                name="check_valid_rport_range",
            )
        ]

        indexes = [
            Index(fields=['user', 'status'], name='user_status_idx'),
            Index(fields=['connected_at'], name='connect_idx'),
        ]

        permissions = [
            ('can_view_socket_connections', 'Can view socket connections'),
            ('can_disconnect_sockets', 'Can disconnect socket connections'),
        ]

    def __str__(self):
        return f"Connection {self.url} {'active' if self.is_active else 'inactive'}"

    async def disconnect(self):
        """Mark the connection as disconnected."""
        self.disconnected_at = timezone.now()
        self.is_active = False
        await self.asave()
