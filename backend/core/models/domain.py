from django.db.models import CharField, ForeignKey, CASCADE, Model

from backend.core.models.host import Host
from backend.core.models.mixins import CreationDateMixin, UpdateDateMixin


class Domain(Model, CreationDateMixin, UpdateDateMixin):
    tld = CharField()
    host = ForeignKey(
        to=Host,
        on_delete=CASCADE,
    )

    class Meta:
        app_label = 'core'
        verbose_name = 'Domain Name'
        verbose_name_plural = 'Domain Names'

