from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import JSONField
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class Settings(models.Model):
    """
    Represents a configurable application or framework setting.

    The AHSSettings model is designed to store key-value pairs representing ahs_settings
    for the application or specific modules. Settings can be of different types
    (e.g., AHS or Django ahs_settings), and include optional descriptions, activity
    status, and the ability to categorize based on modules. This model allows for
    effective management of application configurations.

    Attributes:
        type: A string field that specifies the type of the setting. Choices are
            "ahs_core" for AHS Setting or "django" for Django Setting.
        key: A unique string field representing the key or name of the setting.
        value: A text field storing the value of the setting as a string.
        description: An optional text field providing a descriptive summary of the
            setting's purpose.
        is_active: A boolean field indicating whether the setting is active. Defaults
            to True.
        created_at: A datetime field automatically set when the setting is created.
        updated_at: A datetime field automatically updated when the setting is modified.
        updated_by: A foreign key to :model:`ahs_core.User` indicating the user
            who last updated this setting.
        module: An optional string field representing the module or feature to
            which this setting belongs.

    Meta:
        app_label: The app label for the model is set to "ahs_core".
        verbose_name: A human-readable name for this model is "AHS Setting".
        verbose_name_plural: The plural form of the model's name is "AHS Settings".

    Methods:
        __str__:
            Returns a string representation of the setting in the format
            "key: value".
    """
    TYPE_CHOICES = [
        ("ahs_core", "AHS Setting"),
        ("django", "Django Setting"),
    ]

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        help_text=_("The type of setting configuration (e.g., AHS or Django)."),
    )

    key = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("The key or name of the setting."),
    )

    value = JSONField(
        default=dict,
        help_text=_("The value of the setting stored as a JSON object."),
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text=_("Optional description of the setting and its purpose."),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Determines if the setting is currently active."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    module = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("The module or feature this setting belongs to."),
    )


    class Meta:
        app_label = "ahs_core"
        db_table = "ahs_core_settings"
        verbose_name = _("AHS Setting")
        verbose_name_plural = _("AHS Settings")
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.value}"


