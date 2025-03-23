from django.contrib.sessions.base_session import BaseSessionManager
from django.db.models import CharField, Model, DateTimeField
from django.utils.translation import gettext as _


class AHSBaseSession(Model):
    session_token = CharField(_("session token"), max_length=511)
    expire_date = DateTimeField(_("expire date"), db_index=True)

    objects = BaseSessionManager()

    class Meta:
        abstract = True
        db_table = "django_session_ahs"
        verbose_name = _("ahs session")
        verbose_name_plural = _("ahs sessions")

    def __str__(self):
        return self

    def get_decoded(self):
        session_store_class = self.get_session_store_class()
        return session_store_class.decode(self.session_token)

    @classmethod
    def get_session_store_class(cls):
        raise NotImplementedError

