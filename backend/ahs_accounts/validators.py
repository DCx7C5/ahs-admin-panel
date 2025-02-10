import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class AHSUsernameValidator(validators.RegexValidator):
    regex = r"^[a-zA-Z0-9._-]+\Z"
    message = _(
        "Enter a valid username. This value may contain only unaccented lowercase a-z "
        "and uppercase A-Z letters, numbers, and @/./+/-/_ characters."
    )
    flags = re.ASCII

