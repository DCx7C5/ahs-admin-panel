from django.db.models import Model
from django.db.models.fields import CharField, UUIDField, SlugField, BooleanField
from django.utils.text import slugify
import uuid


class Page(Model):
    name = CharField(max_length=255, unique=True)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    slug = SlugField(max_length=255, unique=True, blank=True, null=True)
    web_socket = BooleanField(default=False)

    class Meta:
        app_label = 'core'
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['name']

    async def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        await super().asave(*args, **kwargs)

    def __str__(self):
        return self.name
