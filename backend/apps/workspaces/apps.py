from django.apps import AppConfig


class WorkspacesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.workspaces'

    def ready(self):
        pass
