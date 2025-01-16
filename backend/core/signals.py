from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.core.models.workspace import Workspace

AHSUser = get_user_model()


@receiver(post_save, sender=AHSUser)
async def create_default_workspace(sender, instance, created, **kwargs):
    if created:  # Only create workspace for newly created users
        await Workspace.objects.acreate(
            owner=instance,
            default=True  # Optional: Make it the default workspace
        )
