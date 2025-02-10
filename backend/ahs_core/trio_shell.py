
from trio.socket import SocketType, socket


class SocketFactory:
    @classmethod
    async def create(cls, sfamily: int, stype: int, *args, **kwargs) -> SocketType:
        return socket(sfamily, stype, *args, **kwargs)



class ConnectionManager:
    def __init__(self):
        self.connections = {}


class App:
    def __init__(self, scope):
        self.scope = scope

    async def __call__(self, receive, send):
        await send({
            'type': 'http.response.start',
            'status': 200,
            'headers': [
                [b'content-type', b'text/plain'],
            ],
        })
        await send({
            'type': 'http.response.body',
            'body': b'Hello, world!',
        })
