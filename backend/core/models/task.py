import logging

from django.db import models
from django.db.models import Model, ForeignKey
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class TaskStatus:
    """
    Represents the various lifecycle states of a Task.

    Available task statuses:
    - **Pending:** Task is awaiting execution (:filter:`pending`).
    - **Running:** Task is currently in progress (:filter:`running`).
    - **Success:** Task executed successfully.
    - **Failure:** Task execution failed.
    - **Scheduled:** Task is scheduled for execution at a later time.

    **Usage:**
    Use `TaskStatus` to validate or classify task statuses.

    Example:
        .. code:: python

            if TaskStatus.is_success(TaskStatus.success()):
                # Do something if the task is successful

    Links:
    - Status validation: :model:`core.TaskStatus.is_valid`
    - Pending state check: :model:`core.TaskStatus.is_pending`
    """
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILURE = 'failure'
    SCHEDULED = 'scheduled'

    CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
        (SCHEDULED, 'Scheduled'),
    )

    @classmethod
    def choices(cls):
        return cls.CHOICES

    @classmethod
    def pending(cls):
        return cls.PENDING

    @classmethod
    def running(cls):
        return cls.RUNNING

    @classmethod
    def scheduled(cls):
        return cls.SCHEDULED

    @classmethod
    def success(cls):
        return cls.SUCCESS

    @classmethod
    def failure(cls):
        return cls.FAILURE

    @classmethod
    def is_valid(cls, status):
        return status in dict(cls.CHOICES)

    @classmethod
    def is_pending(cls, status):
        return status == cls.PENDING

    @classmethod
    def is_running(cls, status):
        return status == cls.RUNNING


class Task(Model):
    """

    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    host = ForeignKey(
        to='core.Host',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=255,
        choices=TaskStatus.choices(),
        default=TaskStatus.pending(),
    )

    worker = ForeignKey(
        to='core.Worker',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']

    def clean(self):
        # Ensure status is valid
        if not TaskStatus.is_valid(self.status):
            raise ValidationError({'status': _('Invalid status value.')})
