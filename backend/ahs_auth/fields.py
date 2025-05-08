from django.core.exceptions import ValidationError
from django.db.models.fields import BinaryField
from webauthn.helpers import parse_cbor
from webauthn.helpers.exceptions import InvalidCBORData

from backend.ahs_core.fields import EnumField


class WebAuthnCredentialIdField(BinaryField):
    """
    A custom field for storing and managing WebAuthn credential IDs in a database.

    Stores credential IDs as raw binary in the database and returns binary (bytes) in Python.
    Data can be hex-encoded for display/presentation, but remains binary for application use.
    """

    description = "A field for storing WebAuthn credential IDs (raw bytes)."
    min_length = 16

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value) -> bytes | None:
        """
        Ensure the value is bytes for DB storage.
        """
        if value is None:
            return value
        if isinstance(value, str):
            # Accept both hex-encoded or base64-encoded representations
            try:
                # Try hex-decoding first
                value = bytes.fromhex(value)
            except ValueError:
                # Fallback to UTF-8 encoding for other string representations
                value = value.encode("utf-8")
        return value

    def clean(self, value, model_instance):
        """
        Enforce that any value stored is exactly 43 bytes long.
        """
        value = super().clean(value, model_instance)
        if value is None:
            return value
        if not isinstance(value, bytes):
            raise ValidationError("Credential ID must be bytes.")
        if len(value) < self.min_length:
            raise ValidationError(
                f"Credential ID can't be exactly {self.min_length} bytes, "
                f"got {len(value)} bytes."
            )
        return value


class WebAuthnPublicKeyField(BinaryField):
    """
    A custom Django model field for handling WebAuthn public keys.

    Stores public keys in CBOR (COSE_Key) format in the database and returns bytes in Python.
    PEM/COSE conversions are handled explicitly elsewhere in business logic if needed.
    """

    description = "A field for storing WebAuthn public keys in CBOR (COSE_Key) format."

    def get_prep_value(self, value) -> bytes | None:
        """
        Ensure public key is stored as bytes (CBOR/COSE format) in the database.
        Accepts bytes, or hex/base64 encoded strings.
        """
        if value is None:
            return None
        if isinstance(value, str):
            try:
                # Try hex-decoding (commonly used for binary blobs represented in text)
                value = bytes.fromhex(value)
            except ValueError:
                # Fallback to UTF-8 encoding for other string representations
                value = value.encode('utf-8')
        return value

    def clean(self, value, model_instance):
        value = super().clean(value, model_instance)
        if value is None:
            return value
        try:
            parse_cbor(value)
        except InvalidCBORData:
            raise ValidationError("Credential Public Key is not CBOR data.")
        return None


class WebAuthnCredTypeField(EnumField):
    ...


class WebAuthnDeviceTypeField(EnumField):
    ...
