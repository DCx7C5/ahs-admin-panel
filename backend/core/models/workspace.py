import logging

from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, CASCADE, BooleanField, Model

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
        app_label = 'core'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
