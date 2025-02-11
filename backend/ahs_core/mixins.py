import logging
from django.db.models import DateTimeField, ForeignKey, CASCADE


logger = logging.getLogger(__name__)


class CreationDateMixin:
    """
    A mixin class for managing object creation timestamps.

    This class provides a `created_at` attribute that automatically records
    the datetime when an object of a model is created. This is achieved using
    Django's `DateTimeField` with the `auto_now_add` option set to True.
    It is typically used in models where tracking the creation time of an
    object is required.

    Attributes:
        created_at: DateTimeField that stores the timestamp when the object
        was created. Automatically set to the current datetime on object
        creation and is immutable thereafter.
    """
    created_at = DateTimeField(auto_now_add=True)


class UpdateDateMixin:
    """
    A mixin to automatically update a datetime field when the model is saved.

    This mixin adds functionality to update a `DateTimeField` automatically
    with the current timestamp whenever the parent model instance is saved.
    It uses the `auto_now` property provided by Django's `DateTimeField`
    to achieve this behavior.

    Attributes:
        updated_at: A `DateTimeField` that stores the timestamp of the last update.
            Automatically set to the current date and time when the model is saved.

    Usage:
        This mixin is intended to be added to a model class to ensure
        the `updated_at` attribute is always updated without requiring
        manual intervention.
    """
    updated_at = DateTimeField(auto_now=True)


class TreeMixin:
    """
    Provides hierarchical structure functionality through parent-child relationships.

    This mixin enables Django models to represent a tree structure, allowing each model
    instance to have a parent and multiple children. It provides methods for hierarchical
    traversal and querying, such as determining root status, presence of children, and
    fetching ancestors or descendants.

    Attributes:
        parent (ForeignKey): A self-referential foreign key to represent the parent node
            of the relationship. Nullable and blankable.

    Methods:
        is_root:
            Determines if this instance is a root node, which does not have a parent.
        has_children:
            Checks if this instance has any child nodes.
        get_ancestors:
            Retrieves the list of all ancestor nodes of this instance, ordered from
            the root node to this instance.
        get_descendants:
            Retrieves the list of all descendant nodes of this instance, including
            children, grandchildren, and beyond.
    """

    parent = ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name='children',
    )

    def is_root(self):
        return not self.parent

    def has_children(self):
        if hasattr(self, 'children'):
            return self.children.exists()

    def get_ancestors(self):
        ancestors = [self]
        current_parent = self.parent

        while current_parent:
            ancestors.insert(0, current_parent)
            current_parent = current_parent.parent

        return ancestors

    def get_descendants(self):
        descendants = []

        for child in self.children.all():  # noqa
            descendants.append(child)
            descendants.extend(child.get_descendant_keys())

        return descendants
