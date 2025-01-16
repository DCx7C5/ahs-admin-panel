from django.db.models import (
    CharField,
    URLField,
    Model,
    IntegerField,
    BooleanField,
    ForeignKey,
    CASCADE,
)
from django.utils.translation import gettext_lazy as _
from backend.core.models.mixins import TreeMixin


class MenuItem(Model, TreeMixin):
    name = CharField(
        max_length=64,
        verbose_name=_("Name"),
        help_text=_("The display name of the menu item."),
    )
    path = URLField(
        max_length=128,
        verbose_name=_("Path"),
        help_text=_("The URL or path this menu item links to.")
    )
    icon = CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Icon"),
        help_text=_("Optional icon class or identifier for the menu item."),
    )
    order = IntegerField(
        default=0,
        verbose_name=_("Order"),
        help_text=_("Order in which this item appears in the menu. Lower numbers appear first."),
    )
    active = BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this menu item is currently active and should be displayed."),
    )
    app_label = CharField(
        max_length=42,
        verbose_name=_("App Label"),
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
        verbose_name=_("Parent"),
        help_text=_("Parent menu item for nested or hierarchical menus."),
    )

    class Meta:
        app_label = "core"
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        ordering = ["order", "name"]
        constraints = [
            # Add unique constraints or other database-level integrity rules if needed.
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
