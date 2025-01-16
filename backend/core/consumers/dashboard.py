import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model

from .cmd_parser import Command, CmdHandlerIns

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

AHSUser = get_user_model()



class AHSAsyncWebSocketConsumer(AsyncJsonWebsocketConsumer):
    apps = ('bookmarks',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    async def connect(self):
        """
        Called when the WebSocket connection is established.
        Set up the PTY and start the subprocess (command/shell).
        """

        await self.accept()
        logger.info(f"WebSocket connection accepted: {self.scope['client']}")

    async def disconnect(self, close_code):
        """
        Called when the WebSocket is disconnected.
        Cleans up resources like PTY and subprocess.
        """
        await self.close(code=close_code)
        logger.info(f"WebSocket connection closed: {self.scope['client']}, code: {close_code}")

    async def receive_json(self, datadict, **kw):
        datad = {
            **datadict,
            "owner": self.scope['user'],
            "channel_name": self.channel_name,
            "send_resp_coro": self.send_json,
            "cb": None,
        }
        cmd = await Command(datad)

    async def check_permissions(self):
        user = self.scope['user']
        if not user.has_module_perms('core'):
            await self.send_json(
                {
                    'type': 'error',
                    'message': 'Not authenticated - must be logged in to check permissions.'
                })
            await self.close()
            return False
        return True
