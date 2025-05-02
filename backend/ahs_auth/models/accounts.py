import logging
import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.db.models import ImageField, ManyToManyField
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import UUIDField, DateTimeField, CharField, URLField, BooleanField, EmailField
from django.db.models.indexes import Index

from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.contrib.auth.models import UserManager, PermissionsMixin

from backend.ahs_auth.validators import AHSNameValidator, PublicKeyValidator

logger = logging.getLogger(__name__)


make_publickey = make_password


class AHSUserManager(UserManager):
    """
    Custom user manager for creating asynchronous superusers.

    This class extends the default UserManager to provide custom methods
    for managing the creation of user objects, including a method for
    creating superusers asynchronously with specific default attributes.

    Methods:
        acreate_ahs_superuser: Asynchronously creates a superuser with
        default values for `is_staff` and `is_superuser` set to True.

    """

    async def acreate_ahs_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self._create_user_object(username=username, uid=uuid.uuid4(), password=password, **extra_fields)  # noqa
        await user.asave(using=self._db)

        return user

    acreate_ahs_superuser.alters_data = True


class AHSUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with additional fields and functionality.
    """

    name_validator = AHSNameValidator()
    publickey_validator = PublicKeyValidator()

    AUTHENTICATION_METHOD_CHOICES = (
        ('email', _('E-Mail')),
        ('webauthn', _('WebAuthn')),
        ('keybase', _('Keybase')),
    )

    username = CharField(
        verbose_name=_("username"),
        max_length=32,
        blank=False,
        db_index=True,
        unique=True,
        help_text=_(
            "Required. 32 characters or fewer. Letters, digits and ./-/_ only."
        ),
        validators=[name_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = EmailField(
        verbose_name=_("email address"),
        blank=True,
    )

    first_name = CharField(
        verbose_name=_("first name"),
        max_length=32,
        blank=True,
        validators=[name_validator],
    )

    last_name = CharField(
        verbose_name=_("last name"),
        max_length=150,
        blank=True,
        validators=[name_validator],
    )

    is_staff = BooleanField(
        verbose_name=_("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = BooleanField(
        verbose_name=_("is active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
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

    socket_url = URLField(
        verbose_name=_('Socket URL'),
    )

    date_joined = DateTimeField(
        verbose_name=_("date joined"),
        default=now,
    )

    date_modified = DateTimeField(
        verbose_name=_('last modified'),
        auto_now=True,
    )

    available_auth = ManyToManyField(
        "ahs_auth.AuthMethod",
        verbose_name=_('Available Authentication Methods'),
        help_text=_('Available authentication methods for this user.'),
    )

    objects = AHSUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "ahs_auth"
        verbose_name = _("AHS User Account")
        verbose_name_plural = _("AHS Users Accounts")
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

    def get_absolute_url(self) -> str:
        return reverse(
            'ahs_auth:user-detail',
            kwargs={'pk': self.pk})

