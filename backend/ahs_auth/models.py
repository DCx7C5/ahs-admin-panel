import logging
import uuid
from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.db.models import ImageField
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import UUIDField, DateTimeField, CharField, URLField, BooleanField, EmailField
from django.db.models.indexes import Index


from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, Permission, UserManager, PermissionsMixin

from backend.ahs_auth.validators import AHSNameValidator, PublicKeyValidator


logger = logging.getLogger(__name__)


make_publickey = make_password


class AHSUserManager(UserManager):
    def _create_user_object(self, username, public_key=None, password=None,**extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, **extra_fields)

        if password:
            user.password = make_password(password)
        if public_key:
            user.public_key = make_publickey(public_key)

        return user

    def _create_user(self, username, public_key, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        user = self._create_user_object(username, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, username, public_key, **extra_fields):
        """See _create_user()"""
        user = self._create_user_object(username, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, username, public_key, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, username, public_key, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, username, password, email=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
        self, username, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_superuser.alters_data = True


class AHSUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with additional fields and functionality.
    """
    name_validator = AHSNameValidator()
    publickey_validator = PublicKeyValidator()

    username = CharField(
        verbose_name=_("username"),
        max_length=32,
        unique=True,
        help_text=_(
            "Required. 32 characters or fewer. Letters, digits and ./-/_ only."
        ),
        validators=[name_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = EmailField(_("email address"), blank=True)

    public_key = CharField(
        verbose_name=_('Public Key'),
        validators=[publickey_validator],
        help_text=_('The Users Public key.'),
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
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = BooleanField(
        _("active"),
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
        verbose_name=_('Last Modified'),
        auto_now=True,
    )


    objects = UserManager()
    ahs_objects = AHSUserManager()

    USERNAME_FIELD = "username"
    PUBLICKEY_FIELD = "public_key"
    REQUIRED_FIELDS = []

    class Meta:
        app_label = "ahs_auth"
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

    def get_absolute_url(self) -> str:
        return reverse(
            'ahs_auth:user-detail',
            kwargs={'pk': self.pk})
