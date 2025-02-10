import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class AHSCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.ahs_core'
    verbose_name = 'Project Core'
