import logging
from typing import Any

from django.contrib.sessions.backends.db import SessionStore as DBSessionStore
from django.core import signing




class TokenStore(DBSessionStore):

    def decode(self, session_data):
        """
        Decode the session data.
        """
        # Extend the parent method to add custom logic
        try:
            return signing.loads(
                session_data, salt=self.key_salt, serializer=self.serializer
            )
        except signing.BadSignature:
            logger = logging.getLogger("django.security.SuspiciousSession")
            logger.warning("Session data corrupted")
        except Exception:
            # ValueError, unpickling exceptions. If any of these happen, just
            # return an empty dictionary (an empty session).
            pass
        return {}

    @classmethod
    def get_model_class(cls):
        # Lazy import to avoid circular dependency
        from backend.ahs_core.models import AHSSessionToken
        return AHSSessionToken

    def create_model_instance(self, data):
        """
        Create a new session model with additional fields.
        """
        # Extend the parent method to add custom logic
        session = super().create_model_instance(data)

        return session

    def set_custom_data(self, key, value):
        """Set additional session data."""
        self[key] = value

    def get_custom_data(self, key):
        """Retrieve additional session data."""
        return self.get(key, None)


