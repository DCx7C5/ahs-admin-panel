import uuid
import logging
from django.contrib.sessions.models import Session
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver



logger = logging.getLogger(__name__)


@receiver(post_save, sender=Session, dispatch_uid="create_or_update_session_url")
async def create_or_update_socket_url(*, instance, **kwargs):
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
        surl, created = await UserSocketURL.objects.aupdate_or_create(
            session=instance,
            path=UserSocketURL.encode_path(new_path),
        )
        if created:
            await surl.asave()

    except Exception as e:
        logger.error(f"Error in session signal: {str(e)}")

@receiver(post_delete, sender=Session, dispatch_uid="delete_session_url")
async def delete_socket_url(*, instance, **kwargs):
    try:
        await UserSocketURL.objects.filter(user__session=instance).adelete()
    except Exception as e:
        logger.error(f"Error in session signal: {str(e)}")
