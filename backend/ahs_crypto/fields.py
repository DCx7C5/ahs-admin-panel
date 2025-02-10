from django.db.models.fields import BinaryField
from django.utils.translation import gettext_lazy as _

from backend.ahs_crypto import forms, ecc

from cryptography.hazmat.primitives.asymmetric import ec

from django.db import models

from backend.ahs_crypto.ecc import serialize_private_key_to_der, serialize_public_key_to_der, load_public_key_from_file, \
    deserialize_public_key_from_der, deserialize_private_key_from_der


class EncryptedECCPrivateKeyField(models.BinaryField):
    """
    A custom Django field to store password-protected ECC private keys.
    The private key is encrypted before saving in the database and decrypted when retrieved.
    """

    def to_python(self, value, password: str | bytes = None) -> ec.EllipticCurvePrivateKey | None:
        """
        Convert the database value (encrypted) to a Python object (decrypted private key).
        """
        if value is None:
            return None
        if password is None:
            return None
        elif isinstance(password, str):
            password = password.encode('latin-1')
        if isinstance(value, bytes):
            return deserialize_private_key_from_der(
                private_key_der=value,
                password=password,
            )
        return value

    def get_prep_value(self, value):
        """
        Prepare the Python object (raw private key) for storage in the database (encrypt it).
        """
        if value is None:  # Handle null values
            return None
        # Encrypt the private key before saving it to the database
        return serialize_private_key_to_der(value, )

    def value_to_string(self, obj):
        """
        Serialize the value to a string (e.g., for JSON or fixture export).
        """
        value = self.value_from_object(obj)
        if value is None:
            return ""
        return value.decode("utf-8")  # Assuming data should be base64 encoded, adjust as needed


class ECCPublicKeyField(BinaryField):
    """
    A custom field to handle ECC Public Keys.
    Stores the key as a binary field in the database.
    """
    default_error_messages = {
        "invalid": _("“%(value)s” is not a valid ECC Public Key."),
    }
    description = _("ECC public key")
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 512  # Set a realistic upper bound for public key sizes
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """
        Serialize the value for database storage.
        """
        if value is None:
            return None
        if not isinstance(value, ec.EllipticCurvePublicKey):
            return ecc.serialize_public_key_to_der(value)
        return super().get_prep_value(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Serialize the value into DER when saving in the database.
        """
        if value is None:
            return None
        if isinstance(value, ec.EllipticCurvePublicKey):
            return serialize_public_key_to_der(value)
        return super().get_db_prep_value(value, connection, prepared)

    def to_python(self, value):
        """
        Convert database values back into ECCPublicKey objects.
        """
        if value is None or isinstance(value, ec.EllipticCurvePublicKey):
            return value
        try:
            # Deserialize the value to an ECCPublicKey object
            return deserialize_public_key_from_der(value)
        except ValueError:
            raise ValueError(self.error_messages["invalid"] % {"value": value})

    def formfield(self, **kwargs):
        """
        Provide the custom form field for public keys.
        """
        return super().formfield(
            **{
                "form_class": forms.PublicKeyField,
                **kwargs,
            }
        )