import os
import re

from django.core.exceptions import ValidationError


def validate_md5_hash(value):
    if not re.fullmatch(r"[a-fA-F0-9]{32}", value):
        raise ValidationError("Value must be a valid 32-character MD5 hash.")

def validate_sha256_hash(value):
    if not re.fullmatch(r"[a-fA-F0-9]{64}", value):
        raise ValidationError("Value must be a valid 64-character SHA-256 hash.")


def validate_relative_unix_path(value):
    # Ensure it's a string
    if not isinstance(value, str):
        raise ValidationError('Path must be a string.')
    # Must not start with a slash (should be relative)
    if value.startswith('/'):
        raise ValidationError("Path must be relative and not start with '/'.")
    # Prevent escape from project directory
    if os.path.isabs(value) or value.startswith('../') or '/..' in value:
        raise ValidationError("Path must be relative to the project directory and cannot escape it.")
    # Must only contain valid UNIX-like segments
    if not re.match(r'^([\w\-. ]+/)*[\w\-. ]+$', value):
        raise ValidationError(
            'Enter a valid relative UNIX path (only letters, numbers, _, -, ., and spaces allowed in segments).'
        )


def validate_unix_path(value):
    # Ensure it's a string
    if not isinstance(value, str):
        raise ValidationError('Path must be a string.')
    # Must start with a slash (should be absolute)
    if not value.startswith('/'):
        raise ValidationError('Path must start with /.')
    # Must only contain valid UNIX-like segments
    if not re.match(r'^(/[\w\-. ]+)+/?$', value):
        raise ValidationError(
            'Enter a valid UNIX path (only /, letters, numbers, _, -, ., and spaces allowed in segments).'
        )
