from django.db.models import Manager

from backend.ahs_core.engines import SessionStore
from backend.ahs_core.models.abc import AHSBaseSession


class AHSSessionManager(Manager):
    def encode(self, session_dict):
        """
        Return the given session dictionary serialized and encoded as a string.
        """
        session_store_class = self.model.get_session_store_class()
        return session_store_class().encode(session_dict)

    def save(self, session_dict, expire_date):
        s = self.model(self.encode(session_dict), expire_date)
        if session_dict:
            s.save()
        else:
            s.delete()  # Clear sessions with no data.
        return s


class AHSSession(AHSBaseSession):
    objects = AHSSessionManager()

    @classmethod
    def get_session_store_class(cls):
        return SessionStore