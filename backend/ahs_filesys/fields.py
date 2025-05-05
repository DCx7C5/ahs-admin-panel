from django.core.exceptions import ValidationError
from django.db.models import CharField, IntegerField

from backend.ahs_filesys.validators import validate_relative_unix_path, validate_unix_path, validate_md5_hash, \
    validate_sha256_hash


class MD5HashField(CharField):
    """
    Django field for storing MD5 hashes as strings (32 hexadecimal chars).
    """
    default_validators = [validate_md5_hash]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 32)
        super().__init__(*args, **kwargs)

class SHA256HashField(CharField):
    """
    Django field for storing SHA-256 hashes as strings (64 hexadecimal chars).
    """
    default_validators = [validate_sha256_hash]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 64)
        super().__init__(*args, **kwargs)



class OctalIntegerField(IntegerField):
    """
    Custom Django model field for handling octal integers.

    OctalIntegerField is a subclass of IntegerField that converts input values
    from their octal (base-8) representation to Python integers for storage
    and processing in Django models and databases.

    """
    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value, 8)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')

    def get_prep_value(self, value):
        if value is None:
            return value
        return str(value)


class UnixRelativePathField(CharField):
    """
    A CharField subclass for storing relative Unix file paths.

    This field enforces that the stored value is a valid relative Unix-style file
    path using the `validate_relative_unix_path` validator. The maximum length of
    the stored path is automatically set to 4096 characters unless specified
    otherwise during instantiation.

    Attributes:
        default_validators (list): A list of validators applied to this field,
            which includes `validate_relative_unix_path`.

    Raises:
        ValueError: Raised when attempting to set an invalid relative Unix path
            that does not pass validation.

    Parameters:
        *args: Positional arguments to be passed to the base CharField class.
        **kwargs: Keyword arguments to be passed to the base CharField class.
            The `max_length` keyword argument is set to 4096 by default unless explicitly
            overridden.
    """
    default_validators = [validate_relative_unix_path]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 4096)
        super().__init__(*args, **kwargs)


class UnixAbsolutePathField(CharField):
    """
    Custom field for storing absolute Unix file system paths.

    This field is intended for use in models to store absolute Unix file system
    paths. It ensures that the path is valid and adheres to Unix path standards.
    The field automatically sets a `max_length` of 4096, which is the typical
    maximum length of a Unix path, unless explicitly overridden.

    Attributes:
        default_validators (list): A list containing the :func:`validate_unix_path`
            validator to ensure the stored value is a valid Unix path.

    Raises:
        ValidationError: Raised by the default_validator when the provided path
            is invalid according to Unix path standards.

    Parameters:
        max_length (int): The maximum length of the path. Defaults to 4096 but
            can be overridden by passing a custom value during initialization.
    """
    default_validators = [validate_unix_path]

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 4096)
        super().__init__(*args, **kwargs)


class UnixPathField(CharField):
    """
    A CharField subclass for storing platform-neutral filesystem paths.

    This field is suitable for storing both absolute and relative file system
    paths, independent of the underlying OS (Unix, Windows, etc.). It does
    not enforce any system-specific path validation, allowing maximum flexibility
    for various use-cases that require cross-platform compatibility.

    By default, the maximum length is set to 4096 characters, but it can be
    customized via the `max_length` argument.

    Parameters:
        *args: Standard positional arguments for CharField.
        **kwargs: Standard keyword arguments for CharField (max_length, etc).

    Example:
        path = PathField()
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 4096)
        super().__init__(*args, **kwargs)
