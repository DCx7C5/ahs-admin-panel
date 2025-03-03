import logging

from django.apps import AppConfig



logger = logging.getLogger(__name__)


class CryptoTokenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.ahs_crypto'
    verbose_name = 'Django Cryptography Backend'
