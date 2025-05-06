from django.db.models import (
    Model,
    CharField,
    Index,
    UniqueConstraint,
    Manager,
)
from django.utils.translation import gettext as _


class AuthMethod(Model):
    AUTHMETHOD_TYPE_CHOICES = (
        ('password', 'Password'),
        ('email', 'Email'),
        ('google', 'Google'),
        ('facebook', 'Facebook'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter'),
        ('apple', 'Apple'),
        ('onelogin', 'OneLogin'),
        ('custom', 'Custom'),
        ('webauthn', 'WebAuthn'),
        ('keybase', 'Keybase'),
    )
    name = CharField(
        max_length=255,
        editable=False,
        verbose_name=_("Authentication Method Name"),
        help_text=_("The name of the authentication method."),
        null=False,
        blank=True,
        default='webauthn',
        choices=AUTHMETHOD_TYPE_CHOICES,
    )

    objects = Manager()

    class Meta:
        app_label = "ahs_auth"
        verbose_name = "Authentication Method"
        verbose_name_plural = "Authentication Methods"
        ordering = ['id']
        db_table = "auth_authmethod"

        indexes = [
            Index(fields=['name'], name='authmethod_name_index'),
        ]

        constraints = [
            UniqueConstraint(fields=['name'], name='unique_name_constraint'),
        ]
