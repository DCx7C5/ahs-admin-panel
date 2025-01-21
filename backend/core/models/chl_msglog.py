from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Model,
    Manager,
    ForeignKey,
    CASCADE, JSONField, Q,
)
from django.db.models.constraints import CheckConstraint
from django.db.models.fields import (
    CharField,
    BooleanField,
    DateTimeField, SmallIntegerField,
)
from django.db.models.indexes import Index
from django.utils.translation import gettext_lazy as _


AHSUser = get_user_model()


class CommandLogManager(Manager):
    """
    Manager for managing command log creation.

    This manager is responsible for handling operations related to command logs.
    Its primary function is to provide asynchronous methods for creating log
    entries in an appropriate format with all required attributes.

    Methods
    -------
    async create_log(app_name, func_name, args, kwargs, web_socket: bool = True)
        Creates a log entry for the specified command with the provided arguments.

    """

    async def create_log(self, app_name, func_name, args, kwargs, web_socket=True):
        return await self.acreate(
            app_name=app_name,
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            web_socket=web_socket,
        )


class ChannelLayerMessageLog(Model):
    """
    Represents a log entry for messages sent through a channel layer.

    Provides a detailed record of commands executed via a channel layer, including their status,
    execution metadata, and delivery information. The model can be used to track the lifecycle of
    a message, including retries, errors, and successful delivery. Includes constraints to ensure
    data consistency and useful indexing for querying records efficiently.

    Attributes:
        timestamp: The timestamp when the command was executed.
        status: The status of the message. Choices include ['sent', 'received', 'failed', 'pending'].
        type: The type of the message, e.g., 'command.request'.
        page_name: Reference to the Page where the command was executed.
        app_name: The name of the application that executed the command.
        func_name: The function name of the executed command.
        args: The arguments of the command stored as JSON.
        kwargs: Keyword arguments of the command stored as a JSON object.
        user: The user who executed the command.
        channel_name: The name of the channel or group where the message was sent.
        priority: The priority of the message, where a higher number indicates higher priority.
        is_broadcast: A boolean indicating if the message was broadcast to multiple recipients.
        retry_count: The number of retry attempts for this message.
        delivered_at: The timestamp when the message was successfully delivered.
        error_details: Detailed error information if an error was encountered during processing.

    Constraints:
        - Ensures that `priority` is greater than or equal to 1.
        - Ensures that `retry_count` is greater than or equal to 0.
        - Ensures that `delivered_at` is set only if the `status` is 'sent'.

    Indexes:
        - Index on `timestamp` for efficient chronological sorting and filtering.
        - Composite index on `app_name` and `func_name` for filtering commands by application and function.
        - Index on `user` for filtering records related to a specific user.

    Meta Options:
        - App label is 'core'.
        - Verbose name for admin interface is 'Command Log'.
        - Verbose plural name for admin interface is 'Command Logs'.
        - Default ordering is descending by `timestamp`.
        - The latest item can be retrieved using the `timestamp` field.
    """
    timestamp = DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text=_("The timestamp when the command was executed."),
        db_index=True,
    )

    status = CharField(
        max_length=50,
        choices=[
            ('sent', 'Sent'),
            ('received', 'Received'),
            ('failed', 'Failed'),
            ('pending', 'Pending'),
        ],
        default='pending',
        editable=False,
        help_text=_("The status of the message."),
    )

    type = CharField(
        max_length=48,
        editable=False,
        help_text=_("The type of the message (eg: command.request)."),
    )

    page_name = ForeignKey(
        'core.Page',
        on_delete=CASCADE,
        related_name='command_logs',
        related_query_name='command_log',
        help_text=_("The page where the command was executed."),
    )

    app_name = CharField(
        max_length=48,
        editable=False,
        help_text=_("The app name which executed the command."),
    )

    func_name = CharField(
        max_length=24,
        editable=False,
        help_text=_("The function name of the command."),
    )

    args = JSONField(
        blank=True,
        null=True,
        editable=False,
        help_text=_("The arguments of the command stored as JSON."),
    )

    kwargs = JSONField(
        blank=True,
        null=True,
        editable=False,
        help_text=_("Keyword arguments of the command stored as a JSON object."),
    )

    user = ForeignKey(
        AHSUser,
        on_delete=CASCADE,
        help_text=_("The user who executed the command."),
    )

    channel_name = CharField(
        max_length=255,
        editable=False,
        help_text=_("The name of the channel or group where the message was sent."),
    )

    priority = SmallIntegerField(
        default=1,
        help_text=_("The priority of the message, where a higher number indicates higher priority."),
    )

    is_broadcast = BooleanField(
        default=False,
        help_text=_("Indicates if this message was broadcast to multiple recipients."),
    )

    retry_count = SmallIntegerField(
        default=0,
        editable=False,
        help_text=_("The number of retry attempts for this message."),
    )

    delivered_at = DateTimeField(
        blank=True,
        null=True,
        editable=False,
        help_text=_("The timestamp when the message was successfully delivered."),
    )

    error_details = CharField(
        max_length=1024,
        blank=True,
        null=True,
        editable=False,
        help_text=_("Details of any error encountered during message processing."),
    )
    objects = CommandLogManager()

    class Meta:
        app_label = 'core'
        verbose_name = 'Command Log'
        verbose_name_plural = 'Command Logs'
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'

        constraints = [
            CheckConstraint(
                check=Q(priority__gte=1),  # Ensure priority is >= 1
                name="check_valid_priority",
            ),
            CheckConstraint(
                check=Q(retry_count__gte=0),
                name="check_valid_retry_count",
            ),
            CheckConstraint(
                check=Q(status='sent') | Q(delivered_at__isnull=True),
                name="check_delivered_at_when_sent",
            )
        ]

        indexes = [
            Index(fields=['timestamp'], name='timestamp_idx'),
            Index(fields=['app_name', 'func_name'], name='app_func_name_idx'),
            Index(fields=['status', 'timestamp'], name='status_timestamp_idx'),
            Index(fields=['user'], name='user_idx'),
            Index(fields=['channel_name', 'timestamp'], name='channel_name_timestamp_idx'),
        ]
