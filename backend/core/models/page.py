from django.db.models import Model
from django.db.models.fields import CharField, UUIDField, SlugField
from django.utils.text import slugify
import uuid


class Page(Model):  # Changed to explicit `models.Model` for clarity
    name = CharField(max_length=255, unique=True)  # Ensure page names are unique
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Auto-generate UUID
    slug = SlugField(max_length=255, unique=True, blank=True, null=True)  # Optional slug generation

    class Meta:
        app_label = 'core'
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        ordering = ['name']  # Order pages alphabetically by name

    async def save(self, *args, **kwargs):
        # Automatically generate slug from the name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        await super().asave(*args, **kwargs)

    def __str__(self):
        # String representation for admin panel or shell
        return self.name
