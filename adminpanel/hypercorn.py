import asyncio
import signal
from typing import Any

from hypercorn.config import Config
from hypercorn.trio import serve

from backend.core import AsyncWebsocketTerminal

shutdown_event = asyncio.Event()



def _signal_handler(*_: Any) -> None:
    shutdown_event.set()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)

    loop.run_until_complete(
        serve(AsyncWebsocketTerminal.as_asgi, shutdown_trigger=shutdown_event.wait, mode='asgi',)
    )


    conf = Config()
    conf.bind = ["localhost", 8000]
