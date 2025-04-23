from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import UniqueConstraint, Index, DateTimeField, Manager, Model, ForeignKey, CharField
from django.utils.translation import gettext as _

from backend.ahs_auth.fields import WebAuthnPublicKeyField

User = get_user_model()


class WebAuthnCredentialManager(Manager):
    async def acreate(
            self,
            user: AbstractBaseUser | User,
            cred_id: bytes,
            pub_key: str,
            cred_type: str,
            device_type: str,
            sign_count: int,
            **kwargs,
    ):
        cred = self.model(
            user=user,
            credential_id=cred_id,
            public_key=pub_key,
            credential_type=cred_type,
            device_type=device_type,

            **kwargs
        )
        await cred.asave(using=self._db)
        return cred


class WebAuthnCredential(Model):

    user = ForeignKey(
        "ahs_auth.AHSUser",
        on_delete=models.CASCADE,
        related_name="webauthn_credentials",
        related_query_name="webauthn",
        verbose_name="User",
        help_text=_("The user associated with this credential."),
    )

    credential_id = CharField(
        max_length=255,
        unique=True,
        verbose_name="WebAuthn Credential ID",
        help_text=_("The credential's unique identifier."),
    )

    public_key = WebAuthnPublicKeyField(
        unique=True,
        editable=False,
        verbose_name="WebAuthn Public Key",
        help_text=_("The credential's public key."),
    )

    sign_count = models.IntegerField(
        default=0,
        verbose_name="WebAuthn Sign Count",
        help_text=_("The number of times the credential has been used for sign operations."),
    )

    credential_type = CharField(
        max_length=32,
        editable=False,
        verbose_name="Credential Type",
        help_text=_("The type of credential."),
    )

    device_type = CharField(
        max_length=32,
        editable=False,
        verbose_name="Authenticator Device Type",
        help_text=_("The type of authenticator device."),
    )

    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text=_("The timestamp when the credential was created."),
    )

    objects = WebAuthnCredentialManager()

    class Meta:
        app_label = "ahs_auth"
        verbose_name = "WebAuthn Credential"
        verbose_name_plural = "WebAuthn Credentials"
        ordering = ['id']
        db_table = "auth_accounts_ahsuser_webauthn"
        unique_together = (('user', 'credential_id', 'public_key'),)

        constraints = [
            UniqueConstraint(
                fields=['user', 'credential_id', 'public_key'],
                name='unique_user_cred_id_pub_key_constraint',
            ),
        ]

        indexes = [
            Index(fields=['user'], name='user_index'),
            Index(fields=['credential_id'], name='credential_id_index'),
            Index(fields=['user', 'credential_id'], name='user_credential_id_index'),
            Index(fields=['user', 'credential_id', 'public_key'], name='user_cred_id_pub_key_index'),
        ]
