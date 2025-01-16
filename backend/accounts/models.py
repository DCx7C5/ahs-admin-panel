import uuid

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.db import models



class AHSUser(AbstractUser):
    """
    Simple subclass for custom field extensions of :class: User
    """

    date_modified = models.DateTimeField(
        help_text=_('Last time the user profile was updated'),
        verbose_name='date modified',
        auto_now=True,
        blank=False,
        null=False,
    )

    uid = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        blank=False,
        null=False,
        db_index=True,
        verbose_name=_('User UUID')
    )

    image = models.ImageField(
        verbose_name=_('profile picture'),
        upload_to='pfps',
        default='pfps/default.jpg',
        blank=True,
    )


    class Meta:
        verbose_name = 'AHS User'
        verbose_name_plural = 'AHS Users'

    def pfp(self):
        return mark_safe(f'<img src="/media/{self.image}" width="42" height="42" />')

    pfp.short_description = _('Profile picture')

    def get_absolute_url(self):
        return reverse('ahs_core:profile', kwargs={'username': self.username})

    def __str__(self):
        return self.username

