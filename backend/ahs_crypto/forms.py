from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives import serialization
from django.core.exceptions import ValidationError
from django.forms.fields import CharField
from django.utils.translation import gettext_lazy as _


class PublicKeyField(CharField):
    default_error_messages = {
        "invalid": _("Enter a valid ECC public key."),
    }

    def to_python(self, value):
        value = super().to_python(value)
        if value is None or value.strip() == "":
            return None
        return value

    def validate_public_key(self, public_key):
        try:
            # Attempt to deserialize the public key
            serialization.load_pem_public_key(public_key.encode(), backend=None)
        except (ValueError, TypeError, InvalidKey):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

    def validate(self, value):
        super().validate(value)
        if value:
            self.validate_public_key(value)


class PrivateKeyField(CharField):
    default_error_messages = {
        "invalid": _("Enter a valid ECC private key."),
    }

    def to_python(self, value):
        value = super().to_python(value)
        if value is None or value.strip() == "":
            return None
        return value

    def validate_private_key(self, private_key):
        try:
            # Attempt to deserialize the public key
            serialization.load_pem_private_key(private_key.encode(), backend=None)
        except (ValueError, TypeError, InvalidKey):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

    def validate(self, value):
        super().validate(value)
        if value:
            self.validate_private_key(value)
