import logging
import uuid
from django.apps import apps
from django.contrib.auth.hashers import make_password, verify_password
from django.db.models import ImageField
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import UUIDField, DateTimeField, CharField, URLField
from django.db.models.indexes import Index


from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, Permission, UserManager

from backend.ahs_core.hashers import verify_publickey
from backend.ahs_core.validators import AHSUsernameValidator

logger = logging.getLogger(__name__)


make_publickey = make_password


class AHSUserManager(UserManager):
    def _create_user_object(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        user = self._create_user_object(username, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, username, email, password, **extra_fields):
        """See _create_user()"""
        user = self._create_user_object(username, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(username, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, username, email=None, password=None, **extra_fields):
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

    socket_url = URLField(
        verbose_name=_('Socket URL'),
    )

    public_key = CharField(
        verbose_name=_('Public Key'),
        blank=False,
        null=False,
    )

    objects = AHSUserManager()

    def set_publickey(self, public_key: str) -> None:
        self.public_key = make_publickey(public_key)
        self._public_key = public_key

    def check_publickey(self, public_key):
        is_correct, must_update = verify_publickey(
            publickey=public_key,
            encoded_publickey=self.public_key,
            preferred="default",
        )
        if is_correct and must_update:
            self.set_publickey(public_key)
        return is_correct

    async def acheck_publickey(self, public_key):
        """See check_password()."""

        async def setter(pk):
            self.set_publickey(pk)
            # Password hash upgrades shouldn't be considered password changes.
            self._public_key = None
            await self.asave(update_fields=["password"])

        is_correct, must_update = verify_publickey(
            publickey=public_key,
            encoded_publickey=self.public_key,
            preferred="default",
        )
        if setter and is_correct and must_update:
            await setter(public_key)
        return is_correct

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

    def get_absolute_url(self) -> str:
        return reverse(
            'ahs_core:user-detail',
            kwargs={'pk': self.pk})


    class Meta:
        app_label = "ahs_core"
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
