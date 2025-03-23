from django.contrib.sessions.backends.db import SessionStore as DBSessionStore



class SessionStore(DBSessionStore):

    @classmethod
    def get_model_class(cls):
        # Lazy import to avoid circular dependency
        from backend.ahs_core.models import AHSSession
        return AHSSession

    def create_model_instance(self, data):
        """
        Create a new session model with additional fields.
        """
        # Extend the parent method to add custom logic
        session = super().create_model_instance(data)
        if hasattr(self, 'socket_url'):
            session.socket_url = self.socket_url
        return session

    def set_custom_data(self, key, value):
        """Set additional session data."""
        self[key] = value

    def get_custom_data(self, key):
        """Retrieve additional session data."""
        return self.get(key, None)
