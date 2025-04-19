import base64
import re

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class AHSNameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9_]+\Z"
    message = _(
        "Enter a valid username. This value may contain only unaccented lowercase a-z "
        "and uppercase A-Z letters, numbers, and _ characters."
    )
    flags = re.ASCII


@deconstructible
class PublicKeyValidator(validators.RegexValidator):
    regex = r'^(?:-----BEGIN PUBLIC KEY-----\s*([A-Za-z0-9+/=\s]+)-----END PUBLIC KEY-----\s*$)|(?:^(?:04|02|03)(?:[0-9a-fA-F]{64,128})$)|(?:^[A-Za-z0-9+/]{42,64}={0,2}$)'
    message = _(
        "Not a valid ECC PublicKey."
    )
    flags = re.DOTALL



def validate_base64(value):
    """
    Validator function for checking if a string is valid Base64 encoded data
    """
    # Check if the string follows base64 pattern
    if not re.match('^[A-Za-z0-9+/]*={0,2}$', value):
        raise ValidationError('This is not a valid Base64 string')

    # Try to decode to check if it's properly encoded
    try:
        base64.urlsafe_b64decode(value)
    except Exception:
        raise ValidationError('Invalid Base64 string: decoding failed')


def validate_token(value: str):
    """
    Validator function for checking if a string is a valid token
    """
    # Check if value is a valid string
    if not isinstance(value, str):
        raise ValidationError('Invalid token: not a string')
    # Check token format
    segs = value.split(".")
    header = segs[0]
    if not len(segs) == 3 and header['type'] == 'default':
        raise ValidationError('Invalid token: wrong number of segments')
    # Check if token is properly encoded
    try:
        for seg in segs:
            base64.urlsafe_b64decode(seg)
    except Exception:
        raise ValidationError('Invalid token: decoding failed')

