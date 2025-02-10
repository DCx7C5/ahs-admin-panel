from cryptography.hazmat.primitives.asymmetric import ec
from django.db import models
from django.db.models import ForeignKey, CASCADE

from . import fields
from .ecc import deserialize_private_key_from_der


class PrivateKey(models.Model):
    private_key = fields.BinaryField()

    parent = ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=CASCADE,
        related_name='subkeys',
    )

    def is_root(self):
        """Check if the current private key is the root key."""
        return not self.parent

    def has_children(self):
        """Check if the current private key has child subkeys."""
        return self.subkeys.exists()

    def count_children(self):
        """Count the number of descendant subkeys."""
        return self.subkeys.count()

    def get_ancestors(self):
        """Retrieve all ancestor keys up to the root key."""
        ancestors = [self]
        current_parent = self.parent

        while current_parent:
            ancestors.insert(0, current_parent)
            current_parent = current_parent.parent

        return ancestors

    def get_descendants(self):
        """Retrieve all descendant subkeys of the current key."""
        descendants = []

        for child in self.subkeys.all():
            descendants.append(child)
            descendants.extend(child.get_descendants())

        return descendants

    def create_public_key(self) -> ec.EllipticCurvePublicKey:
        """
        Derive the corresponding public key from the current private key.
        """
        return deserialize_private_key_from_der(self.private_key).public_key()


    class Meta:
        app_label = "ahs_crypto"  # Ensure this matches INSTALLED_APPS
        db_table = "auth_accounts_crypto_privkeys"
        verbose_name = "Private Key"
        verbose_name_plural = "Private Keys"

    indexes = [
        models.Index(fields=['private_key'], name='private_key_idx'),
    ]

    constraints = [
        models.UniqueConstraint(
            fields=['private_key'],
            name='unique_private_key',
        ),
    ]


class PublicKey(models.Model):
    private_key = ForeignKey(
        PrivateKey,
        on_delete=models.CASCADE,
    )
    public_key = fields.BinaryField()



    class Meta:
        app_label = "ahs_crypto"
        db_table = "auth_accounts_crypto_pubkeys"
        verbose_name = "Public Key"
        verbose_name_plural = "Public Keys"

    indexes = [
        models.Index(fields=['public_key'], name='public_key_idx'),
    ]

    constraints = [
        models.UniqueConstraint(
            fields=['public_key'], name='unique_public_key',
        )
    ]
