import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.ahs_socket_conns.models import SocketConnection


logger = logging.getLogger(__name__)


@receiver(post_save, sender=SocketConnection)
async def log_connection_events(sender, instance, created, **kwargs):
    """
    Asynchronous function that listens for `post_save` signals emitted by the
    :model:`app_label.SocketConnection` model instances. It logs connection and
    disconnection events of socket connections, providing details such as
    the user and the timestamps.

    Summary:
    This function is triggered automatically after a `SocketConnection`
    model instance is saved. It distinguishes between connection
    events (when a new instance is created) and disconnection events
    (when the `is_active` state of an instance changes to inactive).
    The relevant information is logged for each event type.

    Args:
        sender (Type[SocketConnection]): The model class that sent the signal.
        instance (SocketConnection): The instance of `SocketConnection` that was saved.
        created (bool): A flag indicating whether the instance was created.
        **kwargs: Additional keyword arguments passed by the signal dispatcher.

    Returns:
        None

    Notes:
        The function assumes that `SocketConnection` instances include the
        fields: `user`, `connected_at`, `disconnected_at`, and `is_active`.

    Raises:
        Does not explicitly raise exceptions but may propagate exceptions
        if issues occur during the signal handling or logging processes.
    """
    if created:
        logger.debug(f"User {instance.user} connected at {instance.connected_at}")

    elif not instance.is_active:
        logger.debug(f"User {instance.user} disconnected at {instance.disconnected_at}")
