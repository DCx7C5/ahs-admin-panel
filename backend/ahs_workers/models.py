import secrets
from django.db import models
from django.db.models import Model, ForeignKey
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from backend.apps.network.models.hosts import Host


class ActiveWorkerException(Exception):
    """Custom exception for Worker management errors."""
    pass


class AsyncWorkerManager(models.Manager):
    """Async manager to handle active ahs_workers."""

    async def register_worker(self, name: str, status: str = "active") -> "Worker":
        """
        Registers a new worker with a unique API key.
        Args:
            name: The worker's name.
            status: Default status for the worker (default: "active").
        Returns:
            Worker: The registered worker instance.
        """
        api_key = secrets.token_hex(16)  # Generate a secure random API key
        worker = Worker(name=name, api_key=api_key, status=status, last_active_time=now())
        await worker.asave()  # Asynchronous save
        return worker

    async def is_valid_api_key(self, api_key: str) -> bool:
        """
        Validates if the given API key corresponds to an active worker.
        Args:
            api_key (str): The API key to validate.
        Returns:
            bool: True if valid; False if invalid.
        """
        try:
            worker = await self.filter(api_key=api_key, status="active").aget()
            return worker is not None
        except Worker.DoesNotExist:
            return False

    async def get_worker_by_api_key(self, api_key: str) -> "Worker":
        """
        Retrieves a worker by their API key if active.
        Args:
            api_key: The API key of the worker.
        Returns:
            Worker: The worker instance.
        Raises:
            ActiveWorkerException: If the worker does not exist or is inactive.
        """
        try:
            return await self.filter(api_key=api_key, status="active").aget()
        except Worker.DoesNotExist:
            raise ActiveWorkerException("Worker with the provided API key not found or inactive.")

    async def mark_inactive(self, api_key: str) -> None:
        """
        Marks a worker as inactive by their API key.
        Args:
            api_key: The API key of the worker to deactivate.
        Raises:
            ActiveWorkerException: If the worker does not exist.
        """
        try:
            worker = await self.filter(api_key=api_key).aget()
            worker.status = "inactive"
            await worker.asave()
        except Worker.DoesNotExist:
            raise ActiveWorkerException("Worker with the provided API key not found.")

    async def get_active_workers(self):
        """
        Retrieves all active ahs_workers.
        Returns:
            QuerySet: A QuerySet of active ahs_workers.
        """
        return await self.filter(status="active").aget()


class Worker(Model):
    """
    Represents a worker in the system with a unique API key
    and activity tracking.
    """
    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=64, unique=True, db_index=True)
    status = models.CharField(
        max_length=32,
        choices=[
            ("active", _("Active")),
            ("inactive", _("Inactive")),
            ("suspended", _("Suspended"))
        ],
        default="active",
    )
    host = ForeignKey(
        to=Host,
        on_delete=models.CASCADE,
        related_name='ahs_workers',
        null=True,
        blank=True,
        default=None
    )
    last_active_time = models.DateTimeField(default=now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AsyncWorkerManager()  # Custom async manager

    class Meta:
        app_label = "ahs_core"
        db_table = "ahs_core_workers"
        verbose_name = _("Worker")
        verbose_name_plural = _("Workers")
        ordering = ["-last_active_time"]

    async def refresh_activity(self):
        """
        Updates the worker's `last_active_time` to the current time.
        """
        self.last_active_time = now()
        await self.asave()

    def clean(self):
        """
        Ensure valid status for the worker.
        """
        valid_statuses = ["active", "inactive", "suspended"]
        if self.status not in valid_statuses:
            raise ValidationError({'status': _("Invalid worker status.")})
