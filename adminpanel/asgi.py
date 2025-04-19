import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.apps import apps  # Import for app registry check
from django.urls import re_path

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Ensure Django apps are initialized before accessing them
django_asgi_app = get_asgi_application()

# Verify apps are ready (optional: helpful for debugging)
if not apps.ready:
    raise RuntimeError("Django apps aren't ready yet!")

# Import consumers lazily after initialization
from backend.ahs_core.consumers.channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from backend.ahs_core.consumers.terminal_dispatcher import AsyncWebsocketTerminal
from backend.ahs_core.consumers.command_dispatcher import AHSCommandConsumer

# Configure protocol routing
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(
                    r"^ws/(?P<socket_url>[0-9a-f-]{36})/$",
                    AsyncJsonWebsocketDemultiplexer.as_asgi(
                        command=AHSCommandConsumer.as_asgi(),
                        terminal=AsyncWebsocketTerminal.as_asgi(),
                    )
                ),
            ])
        )
    ),
})
