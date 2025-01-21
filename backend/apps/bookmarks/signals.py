from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import BookmarksProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
async def create_bookmark_user(sender, instance, created, **kwargs):
    if created:
        await BookmarksProfile.objects.acreate(user=instance)
