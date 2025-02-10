from django.contrib.sessions.backends.db import SessionStore as DBSessionStore
from django.contrib.sessions.models import Session
from django.db.models import UUIDField
from django.db.models.fields import CharField


class AHSSession(Session):
    socket_url = UUIDField(
        editable=False,
        auto_created=True,
        unique=True,
        db_index=True,
        help_text="Unique socket URL identifier for the session."
    )

    class Meta:
        db_table = "django_session"
        app_label = "ahs_sessions"
