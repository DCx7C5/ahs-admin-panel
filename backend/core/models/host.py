import logging
from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
    BooleanField,
    GenericIPAddressField,
    QuerySet,
    Manager,
)

from backend.core.models.abc import AbstractEntity
from backend.core.models.mixins import CreationDateMixin, UpdateDateMixin
from backend.core.models.workspace import Workspace

logger = logging.getLogger(__name__)

class HostManager(Manager):
    async def get_queryset(self) -> QuerySet:
        return await super().aget_queryset()


class RemoteHostManager(Manager):
    async def get_queryset(self) -> QuerySet:
        return await super().aget_queryset().filter(remote=True)

    async def create_rhost(self, address, name, owner, remote=True, *args, **kwargs):
        return await self.acreate(address=address, name=name, owner=owner, remote=remote, *args, **kwargs)

    async def get_or_create_rhost(self, defaults=None, **kwargs) -> "Host":
        return await self.aget_or_create(defaults, **kwargs)


class Host(AbstractEntity, CreationDateMixin, UpdateDateMixin):

    address = GenericIPAddressField(
        verbose_name='host ip address',
        unique=True,
        blank=False,
        protocol='IPv4',
    )
    name = CharField(
        verbose_name='hostname',
        max_length=253,
        unique=True,
        blank=True,
    )

    workspace = ForeignKey(
        to=Workspace,
        on_delete=CASCADE,
    )

    remote = BooleanField(
        verbose_name='is remote host',
    )

    objects = Manager()
    remote_hosts = RemoteHostManager()

    class Meta:
        app_label = 'core'
        verbose_name = 'host'
        verbose_name_plural = 'hosts'
