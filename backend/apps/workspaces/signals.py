import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.apps.workspaces.models import Workspace

User = get_user_model()

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
async def create_default_workspace(*, instance, created, **kwargs):
    """
    Signal receiver that creates a default workspace for a newly created User.

    This signal is triggered after an User instance is saved. If the instance
    is newly created, it will asynchronously create a default workspace associated
    with the instance.

    Parameters
    ----------
    instance : User
        The instance of User that was saved.
    created : bool
        Indicates whether this is a new instance of User.
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
