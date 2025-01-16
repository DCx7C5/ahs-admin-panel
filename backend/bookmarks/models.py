from django.contrib.auth import get_user_model
from django.db.models import (
    DateTimeField,
    CASCADE,
    OneToOneField,
    Model,
    UUIDField,
    URLField,
    ForeignKey,
    CharField,
    ManyToManyField, BooleanField
)
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


User = get_user_model()


class Tag(Model):
    name = CharField(
        max_length=100,
        unique=True,
    )

    bm = ManyToManyField(
        'Bookmark',
        related_name='tags',
    )

    created = DateTimeField(
        verbose_name=_('created on'),
        auto_now_add=True,
    )

    updated = DateTimeField(
        verbose_name=_('last update on'),
        auto_now=True,
    )

    owner = ForeignKey(
        'BookmarksProfile',
        on_delete=CASCADE,
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark tag'
        verbose_name_plural = 'bookmark tags'


class Category(Model):
    name = CharField(
        max_length=100,
        unique=True,
    )

    bm = ManyToManyField(
        'Bookmark',
        related_name='category',
    )

    created = DateTimeField(
        verbose_name=_('created on'),
        auto_now_add=True,
    )

    updated = DateTimeField(
        verbose_name=_('last update on'),
        auto_now=True,
    )

    owner = ForeignKey(
        'BookmarksProfile',
        on_delete=CASCADE,
    )

    uuid = UUIDField(
        unique=True,
        null=False,
        editable=False,
    )

    active = BooleanField(
        default=True,
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark category'
        verbose_name_plural = 'bookmark categories'


class Bookmark(Model):
    name = CharField(
        max_length=500,
        null=False,
    )

    url = URLField(
        null=False,
        max_length=1000,
    )

    created = DateTimeField(
        verbose_name=_('created on'),
        auto_now_add=True,
    )
    
    updated = DateTimeField(
        verbose_name=_('last update on'),
        auto_now=True,
    )
    
    owner = ForeignKey(
        'BookmarksProfile',
        default=None,
        on_delete=CASCADE,
    )

    icon_url = URLField(
        null=True,
        max_length=1000,
    )
    
    uuid = UUIDField(
        unique=True,
        null=False,
        editable=False, 
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark'
        verbose_name_plural = 'bookmarks'

    def icon_tag(self, w: int = 20, h: int = 20):
        if self.icon_url:
            return mark_safe(f'<img src="{self.icon_url}" width="{w}" height="{h}" />')
        if self.url:
            ico_url = f"https://{self.url.split('/')[2]}/favicon.ico"
            return mark_safe(f'<img src="{ico_url}" width="{w}" height="{h}" />')

    icon_tag.short_description = _('Image')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class BookmarksProfile(Model):
    user = OneToOneField(
        to=User,
        on_delete=CASCADE,
        to_field='id',
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark profile'
        verbose_name_plural = 'bookmark profiles'


async def create_bookmark(*args, **kwargs):
    bookmark = await Bookmark.objects.acreate()
