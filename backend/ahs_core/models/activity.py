from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Index, CASCADE, ForeignKey, Model
from django.db.models.fields import DateTimeField, TextField, CharField, PositiveIntegerField
from django.utils import timezone


class Activity(Model):
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

    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['content_type', 'object_id']),
            Index(fields=['created_at']),
        ]
        verbose_name_plural = 'activities'

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
