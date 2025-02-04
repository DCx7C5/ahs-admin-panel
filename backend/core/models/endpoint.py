from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import (
    CharField,
    URLField,
    Model,
    IntegerField,
    BooleanField,
    ForeignKey,
    CASCADE, SET_NULL,
)
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from backend.core.models.mixins import TreeMixin
from backend.core.models.appmodel import AppModel  # Import AppModel


class AHSEndPoint(Model, TreeMixin):
    """
    Represents a menu item in a hierarchical structure that can be displayed in menus,
    sidebars, or navigation components.

    This model provides functionality for organizing menu items into a tree structure
    with parent-child relationships, order tracking, breadcrumb generation, and more.
    A menu item can link to a specific URL or path and optionally have an associated icon,
    application label, or status indicating whether it is active.

    Attributes:
        name: The display name of the menu item.
        path: The URL or path this menu item links to.
        icon: Optional icon class or identifier for the menu item.
        order: Order in which this item appears in the menu. Lower numbers appear first.
        active: Whether this menu item is currently active and should be displayed.
        parent: Parent menu item for nested or hierarchical menus.
        associated_objects: A generic relation to associate with any arbitrary model.
    """

    name = CharField(
        max_length=64,
        verbose_name="Name",
        help_text=_("The display name of the menu item."),
    )

    path = URLField(
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

    order = IntegerField(
        default=0,
        verbose_name="Order",
        help_text=_("Order in which this item appears in the menu. Lower numbers appear first."),
    )

    active = BooleanField(
        default=True,
        verbose_name="Active",
        help_text=_("Whether this menu item is currently active and should be displayed."),
    )

    parent = ForeignKey(
        "self",
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text=_("Parent menu item for nested or hierarchical menus."),
    )

    # Generic relation to AppModel for polymorphic association
    associated_objects = GenericRelation(
        AppModel,
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="endpoints",  # Allows querying associated objects via `.endpoints`
    )

    class Meta:
        app_label = "core"
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ["order", "name"]
        constraints = [
            UniqueConstraint(fields=["name", "parent"], name="unique_name_parent_constraint"),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.__str__()

    def get_url(self):
        """Returns the absolute URL or path of this menu item."""
        return self.path

    @property
    def is_root(self):
        """Checks whether this menu item is a root (no parent)."""
        return self.parent is None

    @property
    def has_children(self):
        """Checks whether this menu item has child items."""
        return self.children.exists()

    async def get_submenu(self):
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
            "name": self.name,
            "path": self.path,
            "icon": self.icon,
            "order": self.order,
            "active": self.active,
            "children": [child.to_react_sidebar_item() for child in self.children.filter(active=True)],
        }