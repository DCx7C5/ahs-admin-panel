import logging

from backend.core.models.abc import AbstractEvent

logger = logging.getLogger(__name__)



class BaseAlert(AbstractEvent):
    recipient = None

    class Meta:
        abstract = True
        ordering = ['-created_at', 'message', 'origin', 'id']
