from django.apps import AppConfig


class AHSSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.system'

    def ready(self):
        ...
