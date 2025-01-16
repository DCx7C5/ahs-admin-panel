import logging
from abc import abstractmethod, ABCMeta
from typing import Any


logger = logging.getLogger(__name__)



class WebSocketPermission:
    """
    Base class for WebSocket permission checks.
    Subclass this to implement custom logic.
    """

    async def has_permission(self, scope: dict, user: Any) -> bool:
        """
        Override this method with your permission logic. Return True to allow connection.
        :param scope: The WebSocket scope containing user and connection details.
        :param user: The user extracted from the scope using 'get_user'.
        """
        if not user.is_authenticated:
            msg = "Not authenticated - must be logged in to check permissions."
            logger.exception(msg)
            raise Exception(msg)
        return True
