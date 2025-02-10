import importlib
import logging
from django.core.exceptions import ImproperlyConfigured
from .settings import ECC_BACKEND
from .ecc import ECC


logger = logging.getLogger(__name__)

if not ECC.check_min_settings():
    raise ImproperlyConfigured("ECC Crypto App is not configured correctly")


