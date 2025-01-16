import logging
from django.db.models import DateTimeField, ForeignKey, CASCADE


logger = logging.getLogger(__name__)


class CreationDateMixin:
    created_at = DateTimeField(auto_now_add=True)


class UpdateDateMixin:
    updated_at = DateTimeField(auto_now=True)


class TreeMixin:
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
            descendants.extend(child.get_descendants())

        return descendants
