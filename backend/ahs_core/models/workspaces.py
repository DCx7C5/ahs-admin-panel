import logging

from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, CASCADE, BooleanField, Model, Manager
from django.db.models.indexes import Index

logger = logging.getLogger(__name__)

User = get_user_model()


class WorkspaceManager(Manager):
    ...



class Workspace(Model):

    owner = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='workspaces',
        related_query_name='workspace',
    )

    default = BooleanField(
        default=False,
        editable=True,
    )

    objects = WorkspaceManager()

    class Meta:
        app_label = 'ahs_core'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'

        indexes = [
            Index(fields=['owner'], name='core_workspace_owner_id_idx'),
        ]
