import base64
import logging
from django.contrib.sessions.models import Session
from django.db.models import Model, OneToOneField, CASCADE, Manager
from django.db.models.fields import CharField


logger = logging.getLogger(__name__)



class SSURLManager(Manager):
    """
    Provides additional methods for managing and querying socket session URLs
    within the database.

    This class is a custom manager that extends the Django ORM `Manager`
    to provide functionality tailored to working with socket session URLs.
    """
    async def get_url(self, session_key: str) -> "SessionSocketURL":
        """Get the socket URL for a session."""
        return await self.filter(session__session_key=session_key).aget()

    async def is_valid_url(self, session_key: str) -> bool:
        """Check if the socket URL is valid."""
        return await self.filter(session_id__exact=session_key).aexists()


class SessionSocketURL(Model):
    """
    Represents a mapping between a session and a unique socket URL.

    This model is used to associate a Django session with a unique socket URL.
    The `SessionSocketURL` model includes functionality to encode and decode
    paths using base64 URL-safe encoding, allowing for secure and unique
    identification of socket connections.
    """
    session = OneToOneField(
        Session,
        on_delete=CASCADE,
        primary_key=True,

    )

    path = CharField(
        max_length=48,
        db_index=True,
        unique=True,
    )

    objects = SSURLManager()

    class Meta:
        app_label = "core"
        db_table = "django_session_socketurl"
        verbose_name = "Session Socket URL"
        verbose_name_plural = "Session Socket URLs"

        permissions = [
            ("use_channnel_layer", "Can use channel layer"),
        ]


    def set_encoded_path(self, path: str):
        """Set a base64-encoded path."""
        self.path = self.encode_path(path)

    def get_decoded_path(self) -> str:
        """Get the decoded value of the path."""
        return self.decode_path(self.path)

    @staticmethod
    def encode_path(path: str) -> str:
        """Encodes a path using base64 URL-safe encoding."""
        return base64.urlsafe_b64encode(path.encode()).decode()

    @staticmethod
    def decode_path(encoded_path: str) -> str:
        """Decodes a base64 URL-safe encoded path."""
        return base64.urlsafe_b64decode(encoded_path.encode()).decode()
