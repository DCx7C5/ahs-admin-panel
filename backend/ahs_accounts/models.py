import logging
import uuid

from cryptography.hazmat.primitives.asymmetric import ec
from django.contrib.auth import get_user_model
from django.db.models import Model, ImageField, CASCADE, OneToOneField
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import UUIDField, DateTimeField, CharField
from django.db.models.indexes import Index


from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, Permission, UserManager

from backend.ahs_accounts.validators import AHSUsernameValidator
from backend.ahs_crypto import get_private_key_model

logger = logging.getLogger(__name__)


PrivateKey = get_private_key_model()
PublicKey = get_private_key_model()


class AHSUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

    def get_superuser(self) -> "AHSUser":
        return self.filter(is_superuser=True).get()

    async def aget_superuser(self) -> "AHSUser":
        return await self.filter(is_superuser=True).aget()


class AHSUser(AbstractUser):
    """
    Custom user model with additional fields and functionality.
    """
    username_validator = AHSUsernameValidator()

    username = CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and ./-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    uid = UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('User UUID'),
    )
    image = ImageField(
        verbose_name=_('Profile Picture'),
        upload_to='pfps',
        default='pfps/default.jpg',
        blank=True,
    )
    date_modified = DateTimeField(
        verbose_name=_('Last Modified'),
        auto_now=True,
    )
    private_key = OneToOneField(
        PrivateKey,
        on_delete=CASCADE,
        related_name='ahsuser_private_key',
    )
    public_key = OneToOneField(
        PrivateKey,
        on_delete=CASCADE,
        related_name='ahsuser_public_key',
    )

    def set_password(self, raw_password):
        """
        Set the user's password and encrypt/update the private key with the password.
        """
        PrivateKey = get_private_key_model()  # noqa

        super().set_password(raw_password)
        sys_privkey = PrivateKey.objects.first()
        private_key = ec.generate_private_key

    objects = AHSUserManager()
    manager = objects

    # Add any other helper methods, as necessary for public key, etc.

    @property
    def permissions(self):
        """
        Returns a set of all permissions available to the user, including:
            - Permissions assigned directly to the user.
            - Permissions assigned through user groups.

        Returns:
            A set of strings in the format: `app_label.permission_codename`.
        """
        if self.is_superuser:
            # Superusers have all permissions
            return Permission.objects.values_list('content_type__app_label', 'codename').order_by()

        # Collect direct permissions
        user_permissions = set(
            self.user_permissions.values_list('content_type__app_label', 'codename')
        )

        # Collect permissions from groups
        group_permissions = set(
            self.groups.values_list(
                'permissions__content_type__app_label',
                'permissions__codename',
            )
        )

        # Return the combined set of permissions
        return {
            f"{app_label}.{codename}" for app_label, codename in user_permissions.union(group_permissions)
        }

    def get_absolute_url(self):
        return reverse(
            'ahs_core:user-detail',
            kwargs={'pk': self.pk})


    class Meta:
        app_label = "ahs_accounts"
        verbose_name = _("AHS User")
        verbose_name_plural = _("AHS Users")
        db_table = "auth_accounts_ahsuser"
        ordering = ['id']

        constraints = [
            UniqueConstraint(
                fields=["username", "uid"],
                name="unique_username_uuid_constraint",
            ),
        ]

        indexes = [
            Index(fields=['username'], name='username_index'),
            Index(fields=['uid'], name='uid_index'),
            Index(fields=['username', 'uid'], name='username_uid_index'),
        ]
