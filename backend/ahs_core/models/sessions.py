
from django.db.models import Manager, DateTimeField, CharField, Model, Index, IPAddressField, GenericIPAddressField
from django.db.models.constraints import UniqueConstraint

from django.utils.translation import gettext as _

from backend.ahs_core.fields import TokenHeaderField


class AHSSessionManager(Manager):
    async def decode(self, token):
        header, _, signature = token.split('.')


    def deserialize(self):
        ...

    async def asave(self, expire_date):
        s = self.model(expire_date)
        await s.asave()
        return s


class AHSSession(Model):
    session_key = CharField(
        verbose_name=_("session key"),
        max_length=40,
        primary_key=True,
    )

    expire_date = DateTimeField(
        verbose_name=_("expire date"),
        db_index=True,
    )

    objects = AHSSessionManager()

    def __str__(self):
        return self

    @classmethod
    def get_session_store_class(cls):
        from backend.ahs_core.engines import AHSSessionStore
        return AHSSessionStore

    class Meta:
        db_table = "django_session_ahs"
        verbose_name = _("ahs session")
        verbose_name_plural = _("ahs sessions")
