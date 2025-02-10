from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    PositiveBigIntegerField,
    TextField,
    JSONField,
    PositiveIntegerField,
    ForeignKey,
    DateTimeField,
    URLField,
    BooleanField,
    CASCADE,
    CharField, Model,
)
from django.utils.translation import gettext as _

from backend.ahs_core.mixins import (
    UpdateDateMixin,
)



class UserProfile(Model, UpdateDateMixin):

    id = PositiveIntegerField(
        primary_key=True,
    )

    username = CharField(
        max_length=15,
        unique=True,
        help_text=_('Username of an XUser'),
    )

    name = CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        help_text=_('Name of an XUser'),
    )

    connection_status = ArrayField(
        base_field=CharField(max_length=19),
        max_length=7,
    )

    joined_x = DateTimeField(
        null=False,
        blank=False,
        auto_now_add=False,
        auto_now=False,
    )

    description = CharField(
        max_length=160,
        null=True,
        blank=True,
        verbose_name='Biography',
        help_text=_('Description/Bio of an XUser'),
    )

    entities = JSONField(
        null=True,
        verbose_name='Description Entities',
    )

    location = CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name='Location',
    )

    pinned_tweet_id = PositiveBigIntegerField(
        verbose_name='Pinned Tweet ID',
    )

    profile_image_url = URLField(
        verbose_name='Profile Image URL',
        null=True,
    )

    protected: bool = BooleanField(default=False)

    public_metrics: JSONField = JSONField()

    url = URLField(
        null=True,
        blank=True,
        max_length=100,
    )

    verified: bool = BooleanField(
        default=False,
    )

    # withheld = JSONField(default=dict[str, int], null=True)

    class Meta:
        app_label = 'xapi'
        verbose_name = 'X User Profile'
        verbose_name_plural = 'X User Profiles'
        unique_together = (('id', 'username'),)
        ordering = (
            'id',
            'username',
            'name',
            'connection_status',
            'joined_x',
            'description',
            'entities',
            'location',
            'pinned_tweet_id',
            'profile_image_url',
            'protected',
            'public_metrics',
            'url',
            'verified',
            'posts',
            # 'withheld',
        )


class Post(Model, UpdateDateMixin):

    id = PositiveBigIntegerField(primary_key=True)

    edit_history_tweet_ids = ArrayField(
        base_field=CharField(max_length=25)
    )
    attachments = JSONField()

    author = ForeignKey(
        UserProfile,
        on_delete=CASCADE,
        related_name='posts',
    )

    text = TextField(max_length=25000, editable=False)



    class Meta:
        app_label = 'xapi'
        verbose_name = 'Post / Tweet'
        verbose_name_plural = 'Posts / Tweets'

        """ordering = (
            'id',
            'text',
            'edit_history_tweet_ids',
            'attachments',
            'author_id',
            'context_annotations',
            'conversation_id',
            'created_at',
            'edit_controls',
            'entities',
            'in_reply_to_user_id',
            'lang',
            'non_public_metrics',
            'organic_metrics',
            'possibly_sensitive',
            'promoted_metrics',
            'public_metrics',
            'referenced_tweets',
            'reply_settings',
            'withheld',
        )"""
