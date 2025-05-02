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
    ManyToManyField, BooleanField, Manager
)
from django.db.models.constraints import UniqueConstraint
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


User = get_user_model()


class Tag(Model):
    """
    Represents tags assigned to :model:`bookmarks.Bookmark`.
    Used to associate specific bookmarks with user-defined labels.

    References:
        - Related bookmarks: `bm` field linked to :model:`bookmarks.Bookmark`.
        - Owner profile: `owner` field linked to :model:`bookmarks.BookmarksProfile`.
    """
    name = CharField(
        verbose_name=_('tag name'),
        help_text=_('Name of the tag. Must be unique.'),
        max_length=100,
        unique=True,
    )

    bm = ManyToManyField(
        'Bookmark',
        verbose_name=_('related bookmarks'),
        help_text=_('Bookmarks associated with this tag.'),
        related_name='tags',
    )

    created = DateTimeField(
        verbose_name=_('Date Created'),
        help_text=_('The date and time when the tag was created.'),
        auto_now_add=True,
    )

    updated = DateTimeField(
        verbose_name=_('Last Updated'),
        help_text=_('The date and time when the tag was last updated.'),
        auto_now=True,
    )

    owner = ForeignKey(
        'BookmarksProfile',
        verbose_name=_('Owner Profile'),
        help_text=_('The profile of the user who owns this tag.'),
        on_delete=CASCADE,
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark tag'
        verbose_name_plural = 'bookmark tags'
        db_table = 'apps_bookmarks_tag'


class Category(Model):
    """
    Represents categories for grouping :model:`bookmarks.Bookmark` collections.

    Attributes:
        - `name`: Name of the category.
        - `bm`: Many-to-many relation with :model:`bookmarks.Bookmark`.
        - `uuid`: Unique identifier for the category.
        - `owner`: ForeignKey relationship to :model:`bookmarks.BookmarksProfile`.
        - `active`: Boolean signaling if the category is active.
    """
    name = CharField(
        verbose_name=_('category name'),
        help_text=_('Name of the category. Must be unique.'),
        max_length=100,
        unique=True,
    )

    bm = ManyToManyField(
        'Bookmark',
        verbose_name=_('associated bookmarks'),
        help_text=_('Bookmarks grouped into this category.'),
        related_name='category',
    )

    created = DateTimeField(
        verbose_name=_('Date Created'),
        help_text=_('The date and time when the category was created.'),
        auto_now_add=True,
    )

    updated = DateTimeField(
        verbose_name=_('Last Updated'),
        help_text=_('The date and time when the category was last updated.'),
        auto_now=True,
    )

    owner = ForeignKey(
        'BookmarksProfile',
        verbose_name=_('Owner Profile'),
        help_text=_('The profile of the user who owns this category.'),
        on_delete=CASCADE,
    )

    uuid = UUIDField(
        verbose_name=_('Unique Identifier'),
        help_text=_('A unique ID automatically generated for this category.'),
        unique=True,
        null=False,
        editable=False,
    )

    active = BooleanField(
        verbose_name=_('Active Status'),
        help_text=_('Indicates whether the category is active or not.'),
        default=True,
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark category'
        verbose_name_plural = 'bookmark categories'
        db_table = 'apps_bookmarks_category'

        constraints = [
            UniqueConstraint(fields=['name', 'owner'], name='unique_name_owner_constraint'),
            UniqueConstraint(fields=['uuid', 'owner'], name='unique_uuid_owner_constraint'),
        ]

class Bookmark(Model):
    """
    Represents an individual Bookmark instance in the system.

    Includes attributes for `name`, `url`, and `icon_url`.

    References:
        - Tags: Linked via :model:`bookmarks.Tag`.
        - Categories: Linked via :model:`bookmarks.Category`.
        - Owner: ForeignKey connected to :model:`bookmarks.BookmarksProfile`.

    Methods:
        - `icon_tag`: Retrieves the `icon_url` or constructs from the bookmark URL.
    """
    name = CharField(
        verbose_name=_('bookmark name'),
        help_text=_('The name given to the bookmark.'),
        max_length=500,
        null=False,
    )

    url = URLField(
        verbose_name=_('bookmark URL'),
        help_text=_('The URL of the bookmark.'),
        null=False,
        max_length=1000,
    )

    created = DateTimeField(
        verbose_name=_('Date Created'),
        help_text=_('The date and time when the bookmark was created.'),
        auto_now_add=True,
    )
    
    updated = DateTimeField(
        verbose_name=_('Last Updated'),
        help_text=_('The date and time when the bookmark was last updated.'),
        auto_now=True,
    )
    
    owner = ForeignKey(
        'BookmarksProfile',
        verbose_name=_('Owner Profile'),
        help_text=_('The profile of the user who owns this bookmark.'),
        default=None,
        on_delete=CASCADE,
    )

    icon_url = URLField(
        verbose_name=_('icon URL'),
        help_text=_('The URL for the bookmark’s associated icon. Optional.'),
        null=True,
        max_length=1000,
    )
    
    uuid = UUIDField(
        verbose_name=_('Unique Identifier'),
        help_text=_('A unique ID automatically generated for this bookmark.'),
        unique=True,
        null=False,
        editable=False,
    )

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark'
        db_table = 'apps_bookmarks_bookmark'
        verbose_name_plural = 'bookmarks'

    def icon_tag(self, w: int = 20, h: int = 20):
        if self.icon_url:
            return mark_safe(f'<img src="{self.icon_url}" width="{w}" height="{h}" />')
        if self.url:
            # Ensure that URL has at least 3 parts
            split_url = self.url.split('/')
            if len(split_url) > 2:
                ico_url = f"https://{split_url[2]}/favicon.ico"
                return mark_safe(f'<img src="{ico_url}" width="{w}" height="{h}" />')
        # Fallback for invalid or incomplete URLs
        return _("No icon available")

    icon_tag.short_description = _('Image')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class BookmarksProfile(Model):
    """
    Represents profiles (users) who own and manage :model:`bookmarks.Bookmark`.

    Links to:
        - User model instance via the `user` field.
        - Associated bookmarks through the `owner` relationship.
    """
    user = OneToOneField(
        to=User,
        on_delete=CASCADE,
        to_field='id',
    )

    objects = Manager()

    class Meta:
        app_label = 'bookmarks'
        verbose_name = 'bookmark profile'
        verbose_name_plural = 'bookmark profiles'
        db_table = 'apps_bookmarks_bookmarksprofile'

