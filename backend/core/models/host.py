import logging

from django.db.models import (
    CharField,
    ForeignKey,
    CASCADE,
    GenericIPAddressField,
    Model, DateTimeField,
)
from django.db.models.fields import UUIDField

from backend.core.models.workspace import Workspace

logger = logging.getLogger(__name__)


class Host(Model):

    address = GenericIPAddressField(
        unique=True,
        blank=False,
        protocol='IPv4',
    )

    hostname = CharField(
        max_length=253,
        unique=True,
        blank=True,
    )

    uuid = UUIDField(
        unique=True,
        editable=False,
        auto_created=True,
    )

    created_at = DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = DateTimeField(auto_now=True, verbose_name="Updated At")

    workspace = ForeignKey(
        to=Workspace,
        on_delete=CASCADE,
        related_name='hosts',
        related_query_name='host',
        null=True,
        blank=True,
    )

    class Meta:
        app_label = 'core'
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        ordering = ["-created_at"]
