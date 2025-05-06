
from django.db.models.fields import BinaryField, UUIDField

from backend.ahs_auth.webauthn import convert_publickey_pem_to_cbor, convert_publickey_cbor_to_pem


class WebAuthnCredentialId(UUIDField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 48)
        super().__init__(*args, **kwargs)


class WebAuthnPublicKeyField(BinaryField):
    """
    A custom Django field to store public keys in PEM format and automatically convert to CBOR when accessed.
    """

    description = "A field for storing public keys in PEM format, with automatic CBOR conversion."

    def __init__(self, *args, **kwargs):
        self.validate_on_save = kwargs.pop("validate_on_save", True)  # Optional validation control
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        return convert_publickey_pem_to_cbor(value)

    def get_prep_value(self, value: bytes | str) -> bytes | None:
        """
            Converts the given CBOR-encoded public key value to PEM format before storing it in the database.
        """
        if value is None:
            return None

        if isinstance(value, str):
            value = value.encode("utf-8")
        return convert_publickey_cbor_to_pem(value)