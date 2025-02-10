import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from backend.ahs_core.consumers.command import Command

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

User = get_user_model()




class AHSCommandConsumer(AsyncJsonWebsocketConsumer):
    """
    Handles WebSocket connections, JSON/Binary data communication, group management,
    and executes custom WebSocket commands.

    This class extends :class:`channels.generic.websocket.AsyncJsonWebsocketConsumer`
    and is designed to facilitate WebSocket handling within the Django Channels framework.
    It manages group messaging, handles permissions, processes client commands, and defines
    responses for various WebSocket interactions.

    Attributes:
        groups (set): A set of WebSocket group names the current connection belongs to.
        channel_layer: A Django Channels construct to facilitate communication through layers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.groups = set()
        self.channel_layer = None

    async def connect(self):
        """
        Establish the WebSocket connection.

        This method validates permissions and connects the client to the WebSocket.
        If validation fails, the WebSocket connection is closed with an appropriate
        error code and reason.

        Raises:
            Exception: If there is a problem during connection setup or permission
            checking.

        Logging:
            Logs connection details for debugging.
        """

        logger.debug(f"CONNECT: {self.scope}")


        try:
            user = self.scope['user']
            url = self.scope['url_route']['kwargs']['socket_url']
            ch_layer = self.channel_layer
            ch_name = self.channel_name

            await self.accept()

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            await self.close(code=400, reason=f"Validation error: {e}")

        except Exception as e:
            logger.error(f"Error while connecting: {e}")
            await self.close(code=400, reason=f"Error while connecting: {e}")
            return

    def add_default_groups(self):
        pass

    async def disconnect(self, close_code):
        """
        Disconnects the WebSocket connection and removes the client from any active groups.

        This method ensures clean-up of WebSocket group membership by calling
        the `channel_layers.group_discard` method for all associated groups.

        Args:
            close_code (int): The numeric code representing the reason for WebSocket disconnection.
        """

        logger.info(f"DISCONNECT: {self.scope['client']} with code {close_code}")

        if hasattr(self, "groups"):
            for group in list(self.groups):
                await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Handles an incoming WebSocket message.

        This method processes messages depending on their type (text or bytes).
        For text-based messages, it attempts to parse JSON payloads and delegates
        them for processing. For binary messages, it forwards the message for
        further handling.

        Args:
            text_data (str, optional): A text WebSocket message.
            bytes_data (bytes, optional): A binary WebSocket message.
            **kwargs (dict): Additional parameters passed to the function.
        """

        logger.debug(f"RECEIVE: {text_data, bytes_data, kwargs, self.channel_layer}")
        if text_data:
            await self.process_text_message(text_data)
        elif bytes_data:
            await self.process_message(bytes_data)

    async def process_text_message(self, text_data):
        """
        Processes an incoming text WebSocket message containing JSON payloads.

        This method parses the input string as JSON data and validates its format.
        If parsing fails, it returns an error message back to the client.

        Args:
            text_data (str): Incoming JSON-formatted text WebSocket message.

        Raises:
            :exception:`json.JSONDecodeError`: Raised if the JSON payload cannot be parsed.
        """

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {text_data}")
            await self.send_json({"error": "Invalid JSON format"})
            return
        logger.debug(f"process_text_message: {data}")
        await self.process_message(data)

    async def process_message(self, byte_data: dict):
        """
        Processes an incoming text WebSocket message containing JSON payloads.

        This method parses the input string as JSON data and validates its format.
        If parsing fails, it returns an error message back to the client.

        Args:
            byte_data (str): Incoming JSON-formatted text WebSocket message.

        Raises:
            :exception:`json.JSONDecodeError`: Raised if the JSON payload cannot be parsed.
        """
        logger.debug(f"process_message0: {byte_data} , {self.scope}")
        msg_type = byte_data.get("type", None)
        data = byte_data.get("data", None)
        if not msg_type:
            await self.send_json({"error": "Missing kwarg in websocket message. ('type')"})
            return
        logger.debug(f"process_message: {byte_data}")
        await self.send_to_channel_layer(byte_data)

    async def send_to_channel_layer(self, message):
        """
        Sends a message asynchronously to the channel layer.

        This method allows dispatching data to channels or channel groups via
        Django Channels' :ref:`channel_layers`.

        Args:
            message (dict): A JSON-serializable dictionary containing the data to send.
        """

        logger.debug(f"SEND_TO_CHANNEL_LAYER: {message}")
        args = self.scope['url_route']['args']
        kwargs = self.scope['url_route']['kwargs']
        if not message.get('channel_name', None):
            message['channel_name'] = self.channel_name




        await self.channel_layer.send(self.channel_name, message)




    async def send_to_websocket(self, message):
        """
        Sends a given message to a WebSocket connection asynchronously.

        This method logs the outgoing message for debugging purposes and then sends
        that message as text data to a WebSocket.

        Args:
            message (str): The message to send to the WebSocket.

        Returns:
            None
        """

        logger.debug(f"SEND_TO_WEBSOCKET: {message}")
        await self.send(text_data=message)

    async def command_request(self, request):
        """
        Handles an inbound WebSocket command.

        Processes the `request` dictionary containing the client's command parameters,
        such as user information, page context, or channel-specific metadata. Once validated,
        a :class:`backend.ahs_core.consumers.command.Command` object is created and executed.

        Args:
            request (dict): A dictionary holding WebSocket command metadata.
        """
        logger.debug(f"COMMAND_REQUEST: {request}")

        try:
            logger.debug(f"datad: {datad}")
            cmd = Command(**datad)
            await cmd.execute()
        except Exception as e:
            logger.exception(f"Error executing command: {e}")

    async def command_register(self, data):
        """
        Registers a command based on the provided data. This function processes the command
        registration asynchronously, handling any necessary internal logic.

        Args:
            data (dict): A dictionary containing the details of the command to register.

        Returns:
            None
        """
        logger.debug(f"COMMAND_REGISTER: {data}")

    async def command_response(self, data):
        """
        Registers a command based on the provided data. This function processes the command
        registration asynchronously, handling any necessary internal logic.

        Args:
            data (dict): A dictionary containing the details of the command to register.

        Returns:
            None
        """
        logger.debug(f"COMMAND_RESPONSE: {data}")
        self.channel_layer.send()
