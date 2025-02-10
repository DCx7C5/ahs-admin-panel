import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from backend.ahs_core.consumers.channelsmultiplexer import AsyncJsonWebsocketDemultiplexer
from backend.ahs_core.consumers.terminal_dispatcher import AsyncWebsocketTerminal
from backend.ahs_core.consumers.command_dispatcher import AHSCommandConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.ahs_config')


django_asgi_app = get_asgi_application()



# Protocol routing
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r"^ws/(?P<socket_url>[0-9a-f-]{36})/$",
                    AsyncJsonWebsocketDemultiplexer.as_asgi(
                        command = AHSCommandConsumer.as_asgi(),
                        terminal = AsyncWebsocketTerminal.as_asgi(),
                    )
                ),
            ])
        )
    ),
})
