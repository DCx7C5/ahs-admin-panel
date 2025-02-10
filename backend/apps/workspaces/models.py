import logging

from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, CASCADE, BooleanField, Model
from django.db.models.indexes import Index

logger = logging.getLogger(__name__)

AHSUser = get_user_model()


class Workspace(Model):

    owner = ForeignKey(
        AHSUser,
        on_delete=CASCADE,
        related_name='workspaces',
        related_query_name='workspace',
    )

    default = BooleanField(
        default=False,
        editable=True,
    )

    class Meta:
        app_label = 'ahs_core'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'

        indexes = [
            Index(fields=['owner'], name='core_workspace_owner_id_idx'),
        ]
