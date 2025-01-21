import logging
import uuid

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.core.models.socket_url import SessionSocketURL
from backend.core.models.workspace import Workspace

AHSUser = get_user_model()

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AHSUser)
async def create_default_workspace(*, instance, created, **kwargs):
    """
    Signal receiver that creates a default workspace for a newly created AHSUser.

    This signal is triggered after an AHSUser instance is saved. If the instance
    is newly created, it will asynchronously create a default workspace associated
    with the instance.

    Parameters
    ----------
    instance : AHSUser
        The instance of AHSUser that was saved.
    created : bool
        Indicates whether this is a new instance of AHSUser.
    kwargs : dict
        Additional arguments passed to the receiver function.

    Raises
    ------
    None

    Related Models
    --------------
    :model:`your_app_label.Workspace`
    """
    if created:
        await Workspace.objects.acreate(
            owner=instance,
            default=True
        )


@receiver(post_save, sender=Session, dispatch_uid="create_or_update_session_url")
async def create_or_update_url(*, instance, **kwargs):
    """
    Signal handler to create or update a SessionSocketURL when a Session instance is saved.

    This signal is triggered upon saving a Session instance and is responsible for updating or
    creating a corresponding SessionSocketURL. It assigns a new UUID-based path to the URL and
    ensures it is saved to the database. If the SessionSocketURL is newly created, it is explicitly
    persisted using the `asave` method.

    This function is designed to handle exceptions gracefully by logging error messages if an
    issue occurs during URL creation or saving.

    Raised exceptions are logged through the application's logging facility to aid in debugging.

    Args:
        instance (Session): The Session instance being saved, sent automatically
            by the save signal.
        **kwargs: Arbitrary keyword arguments passed by the signal, unused in this function.

    Raises:
        Exception: If an error occurs during the update or save operation for the SessionSocketURL.
    """
    try:
        new_path = str(uuid.uuid4())
        surl, created = await SessionSocketURL.objects.aupdate_or_create(
            session=instance,
            path=SessionSocketURL.encode_path(new_path),
        )
        if created:
            await surl.asave()

    except Exception as e:
        logger.error(f"Error in session signal: {str(e)}")


@receiver(post_save, sender=ActiveConnection)
async def log_connection_events(sender, instance, created, **kwargs):
    if created:  # Log connection
        print(f"User {instance.user} connected at {instance.connected_at}")
    elif not instance.is_active:  # Log disconnection
        print(f"User {instance.user} disconnected at {instance.disconnected_at}")
