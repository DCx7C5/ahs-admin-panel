from django.apps import AppConfig


class AHSSocketConnectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.ahs_network.socket_conns'

    def ready(self):
        from . import signals

