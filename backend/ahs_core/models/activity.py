from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Index, CASCADE, ForeignKey, Model
from django.db.models.fields import DateTimeField, TextField, CharField, PositiveIntegerField
from django.utils import timezone


class Activity(Model):
    """
    Represents an activity or event associated with a user and a specific object.

    The `Activity` model is a generic activity logging system that tracks user actions
    (e.g., create, update, delete, etc.) on various content types in the application.
    It is designed to provide detailed records of user interactions with objects,
    such as posting a comment, liking an item, or updating content.

    Attributes:
        user: A foreign key referring to the user who performed the activity.
        content_type: A foreign key to the content type for the object being acted upon.
        object_id: A positive integer referencing the primary key of the object.
        content_object: A generic foreign key to the related object of the activity.
        action: A char field representing the action taken, such as 'create', 'update', etc.
        description: An optional text field providing additional details about the activity.
        created_at: A datetime field denoting when the activity was created.

    Metadata:
        ordering: Orders the activity records by the `created_at` date in descending order.
        indexes: Includes indexes for efficient lookup based on content type, object ID,
        and creation time.
        verbose_name_plural: Specifies the plural form of the model's name as 'activities'.

    Methods:
        log: Class method to log a new activity with a user, action, object, and
        optional description.
        get_object_activities: Class method to retrieve all activity logs associated
        with a specific object.
    """
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=CASCADE,
        related_name='activities'
    )

    content_type = ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='activities'
    )
    object_id = PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Activity metadata
    action = CharField(
        max_length=50,
        choices=[
            ('create', 'Created'),
            ('update', 'Updated'),
            ('delete', 'Deleted'),
            ('comment', 'Commented'),
            ('like', 'Liked'),
        ]
    )
    description = TextField(blank=True)
    created_at = DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} {self.action} {self.content_object}"

    @classmethod
    def log(cls, user, action, obj, description=''):
        """
        Helper method to easily create activity logs
        """
        return cls.objects.create(
            user=user,
            content_object=obj,
            action=action,
            description=description
        )

    @classmethod
    def get_object_activities(cls, obj):
        content_type = ContentType.objects.get_for_model(obj)
        return cls.objects.filter(
            content_type=content_type,
            object_id=obj.id
        )

    class Meta:
        app_label = 'ahs_core'
        db_table = 'ahs_core_activity'
        verbose_name = 'activity'
        verbose_name_plural = 'activities'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['content_type', 'object_id']),
            Index(fields=['created_at']),
        ]
