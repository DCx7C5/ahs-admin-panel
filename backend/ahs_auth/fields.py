from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidKey
from django.db.models.fields import BinaryField, UUIDField


class WebAuthnCredentialId(UUIDField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 36)
        super().__init__(*args, **kwargs)


class WebAuthnPublicKeyField(BinaryField):
    """
    A custom Django field to store public keys in PEM format and automatically convert to CBOR when accessed.
    """

    description = "A field for storing public keys in PEM format, with automatic CBOR conversion."

    def __init__(self, *args, **kwargs):
        self.validate_on_save = kwargs.pop("validate_on_save", True)  # Optional validation control
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        """
        Validate the PEM format of the public key before saving to the database.
        """
        if self.validate_on_save and value:
            try:
                serialization.load_pem_public_key(value.encode())
            except (ValueError, InvalidKey):
                raise ValueError(f"Invalid public key in {self.attname}.")
        return super().validate(value, model_instance)
