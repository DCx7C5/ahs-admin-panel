import os
from django.core.asgi import get_asgi_application
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from backend.core.consumers.terminal import AsyncWebsocketTerminal
from backend.core.consumers.dashboard import AHSAsyncWebSocketConsumer


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.ahs_config')


django_asgi_app = get_asgi_application()



# Protocol routing
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r"^ws/(?P<room_name>[a-zA-Z]+)/(?P<pty>pty[0-9]{1,5})/$",
                        AsyncWebsocketTerminal.as_asgi()),
                re_path(r"^ws/dashboard/$", AHSAsyncWebSocketConsumer.as_asgi())
            ])
        )
    ),
})
