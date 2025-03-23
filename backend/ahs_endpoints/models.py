from django.db.models import (
    URLField,
    Model,
    BooleanField,
    ForeignKey,
    SET_NULL,
    DateTimeField,
    CharField,
    OneToOneField,
    CASCADE,
    Manager,
    SmallIntegerField, F, Q,
)
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models.indexes import Index
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from backend.ahs_core.models.mixins import TreeMixin
from backend.ahs_core.models.apps import App


class EndPointManager(Manager):
    async def get_sidebar_endpoints(self):
        """
        Asynchronously fetches active root menu items with their children for rendering a sidebar or menu.
        """
        # Fetch root ahs_endpoints (parent is null and active)
        sidebar_items = []

        async for endpoint in self.filter(parent__isnull=True, active=True).order_by("order").all():
            # Fetch children for each root endpoint asynchronously
            sidebar_items.append({
                "id": endpoint.id,
                "path": endpoint.path,
                "icon": endpoint.icon,
                "order": endpoint.order,
                "active": endpoint.active,
                "children": [
                    {
                        "id": child.id,
                        "path": child.path,
                        "icon": child.icon,
                        "order": child.order,
                        "active": child.active
                    } async for child in endpoint.children.filter(active=True).order_by("order").all()
                ]
            })
        return sidebar_items

    async def get_breadcrumb_by_path(self, path):
        """
        Asynchronously builds a breadcrumb structure for a given `path`.
        """
        try:
            # Fetch the endpoint matching the given path asynchronously
            endpoint = await self.aget(path=path)
        except self.model.DoesNotExist:
            return []  # Return an empty breadcrumb if the path does not exist

        breadcrumb = []
        current_item = endpoint

        # Traverse the hierarchy to build the breadcrumb
        while current_item:
            breadcrumb.insert(0, {
                "id": current_item.id,
                "path": current_item.path,
                "name": str(current_item)
            })
            # Fetch parent asynchronously if it is accessed indirectly
            current_item = await current_item.parent()

        return breadcrumb

    async def get_active_endpoints(self):
        """
        Fetches all active ahs_endpoints ordered by the `order` field asynchronously.
        """

        return [
            {
                "id": endpoint.id,
                "path": endpoint.path,
                "order": endpoint.order,
                "icon": endpoint.icon,
                "active": endpoint.active
            }
            for endpoint in self.filter(active=True).order_by("order").all()
        ]

    async def get_children(self, parent_id):
        """
        Asynchronously fetch active children for a specific parent, ordered by `order`.
        """

        return [
            {
                "id": child.id,
                "path": child.path,
                "icon": child.icon,
                "order": child.order,
                "active": child.active
            }
            async for child in self.filter(parent_id=parent_id, active=True).order_by("order").all()
        ]

class EndPoint(Model, TreeMixin):
    """
    Represents a menu item in a hierarchical structure that can be displayed in menus,
    sidebars, or navigation components.
    """

    path = URLField(
        unique=True,
        db_index=True,
        max_length=128,
        verbose_name="Path",
        help_text=_("The URL or path this menu item links to."),
    )
    icon = CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Icon",
        help_text=_("Optional icon class or identifier for the menu item."),
    )
    order = SmallIntegerField(
        default=0,
        verbose_name="Order",
        help_text=_("Order in which this item appears in the menu. Lower numbers appear first."),
    )
    active = BooleanField(
        default=True,
        verbose_name="Active",
        help_text=_("Whether this menu item is currently active and should be displayed."),
    )

    app = ForeignKey(
        App,
        on_delete=CASCADE,
        related_name="endpoints",
        related_query_name="endpoint",
        verbose_name="Application",
        help_text=_("The application this menu item belongs to."),)

    parent = ForeignKey(
        "self",
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text=_("Parent menu item for nested or hierarchical menus."),
    )

    def __str__(self):
        return self.path

    def __unicode__(self):
        return self.__str__()

    def get_url(self):
        """Returns the absolute URL or path of this menu item."""
        return reverse("ahs_core:ahs_endpoints", args=[self.path])

    @property
    def is_root(self):
        """Checks whether this menu item is a root (no parent)."""
        return self.parent is None

    @property
    def has_children(self):
        """Checks whether this menu item has child items."""
        return self.children.exists()

    async def get_endpoint_children(self):
        """Return all child items ordered by their display order."""
        return await self.children.filter(active=True).order_by("order").aget()

    def get_breadcrumb(self):
        """Generates a breadcrumb-like structure for the menu hierarchy."""
        breadcrumb = []
        current_item = self
        while current_item:
            breadcrumb.insert(0, current_item)
            current_item = current_item.parent
        return breadcrumb

    def to_react_sidebar_item(self):
        """Converts data into a format usable by React-based sidebars."""
        return {
            "id": str(self.id),
            "path": self.path,
            "icon": self.icon,
            "order": self.order,
            "active": self.active,
            "children": [child.to_react_sidebar_item() for child in self.children.filter(active=True)],
        }

    objects = EndPointManager()
    manager = objects

    class Meta:
        app_label = "ahs_core"
        db_table = "ahs_core_endpoint"
        verbose_name = "AHS Endpoint"
        verbose_name_plural = "AHS Endpoints"

        indexes = [
            # Combined index for parent and order (used for child item fetching)
            Index(fields=["parent", "order"], name="parent_order_idx"),

            # Active index (frequently queried)
            Index(fields=["active"], name="active_idx"),
        ]

        constraints = [
            # Ensure unique 'order' for siblings (same parent)
            UniqueConstraint(fields=["parent", "order"], name="unique_sibling_order"),

            # Ensure parent cannot point to itself
            CheckConstraint(
                check=~Q(parent=F("id")),
                name="prevent_circular_parent"
            ),
        ]


class EndpointHealthCheck(Model):
    """
    Tracks health-related metadata for ahs_endpoints.

    Attributes:
        endpoint (ForeignKey): The related ahs_endpoints.
        status (str): Indicates the current health status of the ahs_endpoints.
        last_checked (datetime): Timestamp of the last health check.
    """
    HEALTH_STATUSES = [
        ("healthy", "Healthy"),
        ("degraded", "Degraded"),
        ("unavailable", "Unavailable"),
    ]

    endpoint = OneToOneField(EndPoint, on_delete=CASCADE, related_name="health_check")
    status = CharField(
        max_length=20,
        choices=HEALTH_STATUSES,
        default="healthy",
        help_text="Current status of the ahs_endpoints's health."
    )
    last_checked = DateTimeField(auto_now=True, help_text="Timestamp of the last health check.")

    task = ForeignKey(
        "Task",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="endpoint_health_check",
        help_text="Task associated with the health check."
    )

    def __str__(self):
        return f"Health of {self.endpoint.path}: {self.status}"

    class Meta:
        app_label = "ahs_core"
        verbose_name = "Endpoint Health Check"
        verbose_name_plural = "Endpoint Health Checks"
