import logging

from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, CASCADE, BooleanField

from backend.core.models.abc import AbstractEntity


User = get_user_model()
logger = logging.getLogger(__name__)


class Workspace(AbstractEntity):

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

    class Meta:
        app_label = 'core'
        verbose_name = 'Workspace'
        verbose_name_plural = 'Workspaces'
