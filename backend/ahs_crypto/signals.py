from django.contrib.sessions.models import Session
from django.db.models.signals import post_save, pre_save, pre_init
from django.dispatch import receiver

from backend.apps.models import App


@receiver(post_save, sender=Session, dispatch_uid="create_or_update_session_url")
async def create_key_pair(sender, instance, created, **kwargs):
    if created:
        await CryptoAccount.objects.acreate(user=instance)
    else:
        await instance.cryptoaccount.asave()


@receiver(pre_init, sender=App, dispatch_uid="create_or_update_session_url")
async def create_key_pair(sender, instance, created, **kwargs):
    if created:
