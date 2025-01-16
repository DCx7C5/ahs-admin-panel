from typing import TypeVar, Tuple, Literal
from hypercorn.trio.tcp_server import TCPServer as HypercornAsgiHTTPServer
from hypercorn.trio.udp_server import UDPServer as HypercornAsgiQUICServer
from daphne.server import Server as DaphneAsgiServer
from django.core.servers.basehttp import WSGIServer as DjangoWsgiServer
from hypercorn.typing import AppWrapper

ServerType = TypeVar('ServerType',
                        HypercornAsgiHTTPServer,
                        HypercornAsgiQUICServer,
                        DaphneAsgiServer,
                        DjangoWsgiServer
                     )

def start_daphne_server(app_name: AppWrapper | str, *args, **kwargs) -> None:
    pass






def server_factory(
        server: Literal['nginx', 'daphne', 'django', 'hypercorn'],
        server_type: Literal['asgi3', 'asgi2', 'wsgi'],
        app_name: str | AppWrapper,
        *args,
        **kwargs
):
    if server_type == 'asgi3':
        return HypercornAsgiQUICServer(*args, app=app_name, **kwargs)
    elif server_type == 'wsgi' or server == 'django':
        return DjangoWsgiServer(*args, app=app_name, **kwargs)
    elif server == 'nginx':
        pass
    if server == 'hypercorn' and server_type == 'asgi2':
        return HypercornAsgiHTTPServer(*args, app=app_name, **kwargs)
    elif server == 'daphne':
        return DaphneAsgiServer(*args, application=app_name, **kwargs)
