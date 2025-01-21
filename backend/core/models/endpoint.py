from django.db.models import (
    CharField,
    URLField,
    Model,
    IntegerField,
    BooleanField,
    ForeignKey,
    CASCADE,
)
from django.db.models.constraints import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from backend.core.models.mixins import TreeMixin


class AHSEndPoint(Model, TreeMixin):
    """Represents a menu item in a hierarchical structure that can be displayed in menus,
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
        app_label: App label associated with this menu item. Matches the owning app's label.
        parent: Parent menu item for nested or hierarchical menus.

    Meta:
        app_label: Core app label for this model.
        verbose_name: Human-readable name for the model in singular form.
        verbose_name_plural: Human-readable name for the model in plural form.
        ordering: Default ordering of menu items by 'order' and then 'name'.
        constraints: Ensures name uniqueness for menu items under the same parent.

    Methods:
        __str__: Returns the display name of the menu item.
        __unicode__: Returns the unicode representation of the menu item.
        get_url: Returns the absolute URL or path of the menu item.
        is_root: Determines if the menu item is a root node with no parent.
        has_children: Checks whether the menu item has child items.
        get_submenu: Retrieves all active child items ordered by display order.
        get_breadcrumb: Generates a breadcrumb structure for the menu hierarchy.
        get_app: Retrieves the app label associated with the menu item, if available.
        to_react_sidebar_item: Transforms the menu item and its children into a
            dictionary format for use in React-based sidebars.
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

    app_label = CharField(
        max_length=42,
        verbose_name="App Label",
        help_text=_("The app label for this menu item. This should match the app label of the app containing the viewset."),
        null=True,
        blank=True,
    )

    parent = ForeignKey(
        "self",
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Parent",
        help_text=_("Parent menu item for nested or hierarchical menus."),
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

    def get_submenu(self):
        """Return all child items ordered by their display order."""
        return self.children.filter(active=True).order_by("order")

    def get_breadcrumb(self):
        """Generates a breadcrumb-like structure for the menu hierarchy."""
        breadcrumb = []
        current_item = self
        while current_item:
            breadcrumb.insert(0, current_item)
            current_item = current_item.parent
        return breadcrumb

    def get_app(self):
        if self.app_label:
            return self.app_label
        return None

    def to_react_sidebar_item(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "path": self.path,
            "icon": self.icon,
            "order": self.order,
            "active": self.active,
            "appLabel": self.app_label,
            "children": [child.to_react_sidebar_item() for child in self.children.filter(active=True)],
        }
