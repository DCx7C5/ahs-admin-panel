from django.db.models import Model
from django.db.models.fields import CharField, UUIDField, SlugField, BooleanField
from django.utils.text import slugify
import uuid


class Page(Model):
    """
    Represents a web page with metadata and active state.

    This model is used to store information about web pages, including their name,
    UUID, slug, and other properties. It can be used in various contexts where
    web page information and configurations need to be managed or displayed.
    """
    name = CharField(max_length=255, unique=True)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    slug = SlugField(max_length=255, unique=True, blank=True, null=True)
    web_socket = BooleanField(default=False)
    is_active = BooleanField(default=True)

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
