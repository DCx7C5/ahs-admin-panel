import logging
import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.db.models import ImageField
from django.db.models.constraints import UniqueConstraint
from django.db.models.fields import UUIDField, DateTimeField, CharField, URLField
from django.db.models.indexes import Index


from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser, Permission

from backend.ahs_core.validators import AHSUsernameValidator

logger = logging.getLogger(__name__)



class AHSUserManager(BaseUserManager):
    async def create_user(self):
        pass


class AHSUser(AbstractUser):
    """
    Custom user model with additional fields and functionality.
    """
    password = None
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
