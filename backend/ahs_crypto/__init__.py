from django.core.exceptions import ImproperlyConfigured

from .engine import check_min_settings
from .ecc import ECC

if not check_min_settings():
    raise ImproperlyConfigured("Cryptography App is not configured correctly. "
                               "Check CRYPTO_BACKEND setting.")
