## Taken from https://github.com/hishnash/channelsmultiplexer
## Author: hishnash
## RawFile: https://raw.githubusercontent.com/hishnash/channelsmultiplexer/refs/heads/master/channelsmultiplexer/demultiplexer.py

from functools import partial

from asgiref.compatibility import guarantee_single_callable
from channels.consumer import get_handler_name
from channels.generic.websocket import AsyncJsonWebsocketConsumer

import asyncio


class AsyncJsonWebsocketDemultiplexer(AsyncJsonWebsocketConsumer):
    """
    A WebSocket Demultiplexer to handle streams for multiple upstream applications.

    This class extends :class:`channels.generic.websocket.AsyncJsonWebsocketConsumer`
    to provide a framework for multiplexing and routing WebSocket messages across multiple
    upstream applications. It allows handling multiple independent application streams
    by demultiplexing incoming WebSocket frames and dispatching them to the appropriate
    application stream.

    The class enables upstream and downstream communication between a WebSocket client
    and multiple applications by handling connections, disconnections, and message routing.
    It supports text and binary data transformations and provides utilities to manage
    upstream application life cycles. Moreover, applications connected to the multiplexed
    channels can signal WebSocket life cycle events like accept and close, which are
    aggregated by the demultiplexer for communication with the WebSocket client.

    Attributes:
    - `applications` (dict): Mapping of stream names to asynchronous callable applications.
      These applications handle specific streams of WebSocket communication.
    - `application_close_timeout` (int): Timeout in seconds while waiting for upstream applications
      to close before forcefully terminating the connection.

    Parameters:
    - **kwargs (dict): Keyword arguments mapping stream names to application callables.

    Raises:
    - ValueError: Raised for invalid or malformed frames sent upstream or downstream.

    Methods:
    - `__init__`: Initializes the demultiplexer and assigns the stream name to application mappings.
    - `__call__`: Starts the consumer scope and manages WebSocket and upstream application life cycles.
    - `_create_upstream_applications`: Initializes and starts upstream applications associated
      with the stream names.
    - `send_upstream`: Sends messages upstream to the appropriate or all application streams.
    - `dispatch_downstream`: Routes downstream messages from upstream applications to the demultiplexer.
    - `websocket_connect`: Handles WebSocket connection establishment, broadcasting connect
      messages upstream.
    - `receive_json`: Routes received WebSocket messages to the appropriate stream or raises errors
      for invalid frames.
    - `websocket_disconnect`: Handles WebSocket disconnection events, propagating them upstream.
    - `disconnect`: Waits for all upstream applications to close gracefully or times out after
      `application_close_timeout`.
    - `websocket_send`: Intercepts downstream WebSocket `send` messages, handles text and binary
      payloads, and forwards them as JSON-encoded frames.
    - `websocket_accept`: Intercepts downstream WebSocket `accept` messages and determines if
      streams can process incoming frames.
    - `websocket_close`: Handles downstream WebSocket `close` messages for individual streams or
      terminates the connection for all if no upstream applications are accepting frames.
    """
    applications = {}
    application_close_timeout = 5

    def __init__(self, **kwargs):
        for key, app in kwargs.items():
            self.applications[key] = app

        super().__init__()

    async def __call__(self, scope, receive, send):
        """
        Handles the invocation of the demultiplexer application and its associated
        upstream applications, managing their lifecycle, communication, and
        ensuring cleanup on exit.

        This function facilitates creating child upstream applications, observing
        message streams, and ensuring graceful handling of closures or interruptions
        in the asynchronous lifecycle.

        Attributes:
            application_streams (dict): Maps the application streams corresponding to
                upstream applications.
            application_futures (dict): Tracks `asyncio.Future` objects for each upstream
                application and their lifecycle.
            applications_accepting_frames (set): A set of upstream applications currently
                accepting frames or messages.
            closing (bool): Indicates whether the demultiplexer is in a shutting-down state.

        Parameters:
            scope: A dictionary representing the application scope, which includes context
                information like type, path, or custom configurations.
            receive: An async callable used for receiving messages from the communication
                layer.
            send: An async callable used for sending messages to the communication layer.

        Raises:
            asyncio.CancelledError: If the asyncio ahs_tasks associated with message consumers
                or upstream applications are explicitly canceled.

        Returns:
            None
        """
        self.application_streams = {}
        self.application_futures = {}
        self.applications_accepting_frames = set()
        self.closing = False

        scope = scope.copy()
        scope['demultiplexer_cls'] = self.__class__
        self.scope = scope

        loop = asyncio.get_event_loop()
        # create the child applications
        await loop.create_task(self._create_upstream_applications())
        # start observing for messages
        message_consumer = loop.create_task(super().__call__(scope, receive, send))
        try:
            # wait for either an upstream application to close or the message consumer loop.
            await asyncio.wait(
                list(self.application_futures.values()) + [message_consumer],
                return_when=asyncio.FIRST_COMPLETED
            )
        finally:
            # make sure we clean up the message consumer loop
            message_consumer.cancel()
            try:
                # check if there were any exceptions raised
                await message_consumer
            except asyncio.CancelledError:
                pass
            finally:
                # Make sure we clean up upstream applications on exit
                for future in self.application_futures.values():
                    future.cancel()
                    try:
                        # check for exceptions
                        await future
                    except asyncio.CancelledError:
                        pass

    async def _create_upstream_applications(self):
        """
        Creates and initializes upstream application streams and futures for each application.

        This asynchronous function iterates through the defined applications, wraps each
        application into a single callable if necessary, and sets up an asyncio.Queue for
        each application stream. It also schedules invoking each application's callable
        (using an asyncio task) by providing the scope, a `get` operation on the upstream
        queue, and a partial function for dispatching downstream messages tied to the
        specific application stream.

        Raises:
            Exception: Any unexpected error that occurs during the initialization
                or scheduling of upstream applications.

        Parameters:
            self: The instance of the class that encapsulates the
                '_create_upstream_applications' behavior.

        """
        loop = asyncio.get_event_loop()
        for steam_name, application in self.applications.items():
            application = guarantee_single_callable(application)
            upstream_queue = asyncio.Queue()
            self.application_streams[steam_name] = upstream_queue
            self.application_futures[steam_name] = loop.create_task(
                application(
                    self.scope,
                    upstream_queue.get,
                    partial(self.dispatch_downstream, steam_name=steam_name)
                )
            )

    async def send_upstream(self, message, stream_name=None):
        """
        Asynchronously sends a message to the specified stream or all application streams.

        This method is used to distribute messages to one or more application streams
        in a multiplexed system. If a specific `stream_name` is provided, the message
        is sent to the queue associated with that stream. If no `stream_name` is specified,
        the message is broadcasted to all available application streams. In case the
        specified stream is not mapped, an exception is raised.

        Parameters:
            message: Any
                The message to be sent to the stream(s).
            stream_name: Optional[str]
                The name of the specific stream to which the message should be sent.
                If None, the message is sent to all streams.

        Raises:
            ValueError
                If the specified stream name is invalid or not mapped to an
                application stream.

        Returns:
            None
        """
        if stream_name is None:
            for steam_queue in self.application_streams.values():
                await steam_queue.put(message)
            return
        steam_queue = self.application_streams.get(stream_name)
        if steam_queue is None:
            raise ValueError("Invalid multiplexed frame received (stream not mapped)")
        await steam_queue.put(message)

    async def dispatch_downstream(self, message, steam_name):
        """
        Dispatches a message to the appropriate handler or forwards it downstream.

        This function determines the appropriate handler for a given message by using
        its name and attempts to call it. If the handler is not defined, the message
        is passed further downstream using the base_send method. The actual handler
        is determined dynamically, and it should align with the naming convention
        used by get_handler_name.

        Parameters:
            message: The message object that needs to be processed or dispatched.
            steam_name: The name of the stream associated with this message, used as
                        context when invoking the handler.

        Raises:
            This function doesn't explicitly raise exceptions, but handlers invoked
            within it may raise exceptions as part of their execution.

        Returns:
            None
        """
        handler = getattr(self, get_handler_name(message), None)
        if handler:
            await handler(message, stream_name=steam_name)
        else:
            # if there is not handler then just pass the message further downstream.
            await self.base_send(message)

    # Websocket upstream handlers

    async def websocket_connect(self, message):
        """
        Handle the initial WebSocket connection request.

        This method is called when the WebSocket handshake is successful,
        and a connection is established with the client. It processes the
        incoming WebSocket connection request and forwards it upstream to
        initiate communication with an upstream service or server. The
        method ensures that the WebSocket connection is properly forwarded
        and prepared for message handling.

        Parameters:
            message: dict
                The WebSocket connection request message.

        Raises:
            Exception
                If the upstream connection fails.

        Returns:
            None
        """
        await self.send_upstream(message)

    async def receive_json(self, content, **kwargs):
        """
        Handles the reception of JSON messages, validates the structure, and forwards
        messages to the appropriate upstream application based on stream mapping.

        Validates the content to ensure it is a dictionary that includes both the
        `stream` and `payload` keys. If validation fails or the stream name is not
        recognized, raises an error. Otherwise, processes the message by sending it
        to the correct upstream application specified by the stream name.

        Attributes
        ----------
        applications_accepting_frames : set
            A set of stream names that are allowed to receive frames.

        Parameters
        ----------
        content : dict
            The received message, expected to contain `stream` and `payload` keys.
        kwargs : Any
            Additional options passed to the method.

        Raises
        ------
        ValueError
            If the received frame is invalid or the stream name is not mapped.

        Returns
        -------
        None
        """
        # Check the frame looks good
        if isinstance(content, dict) and "stream" in content and "payload" in content:
            # Match it to a channel
            steam_name = content["stream"]
            payload = content["payload"]
            # block upstream frames
            if steam_name not in self.applications_accepting_frames:
                raise ValueError("Invalid multiplexed frame received (stream not mapped)")
            # send it on to the application that handles this stream
            await self.send_upstream(
                message={
                    "type": "websocket.receive",
                    "text": await self.encode_json(payload)
                },
                stream_name=steam_name
            )
            return
        else:
            raise ValueError("Invalid multiplexed **frame received (no channel/payload key)")

    async def websocket_disconnect(self, message):
        """
        Handle the WebSocket disconnect event.

        This method ensures proper cleanup and handling of a WebSocket disconnection.
        When a client disconnects, the method sets a flag to prevent sending a downstream
        `websocket.close` message due to all child applications being closed.
        It also propagates the disconnection event to the upstream and ensures that
        parent class logic is executed for handling the disconnection.

        Parameters:
            message (dict): The message received that indicates the WebSocket has been disconnected.

        Raises:
            Any exceptions or errors raised by the parent class implementation of the
            `websocket_disconnect` method.
        """
        # set this flag so as to ensure we don't send a downstream `websocket.close` message due to all
        # child applications closing.
        self.closing = True
        # inform all children
        await self.send_upstream(message)
        await super().websocket_disconnect(message)

    async def disconnect(self, code):
        """
        Handles the disconnection process for an asynchronous application client.

        This method ensures proper cleanup upon disconnection by waiting for all application-level futures to complete
        or for the application close timeout to expire. If the timeout is reached, any remaining ahs_tasks are forcibly stopped.

        Parameters:
            code (int): The disconnection code representing the reason for disconnecting.

        Raises:
            asyncio.TimeoutError: If the disconnection process exceeds the specified timeout period.
        """
        try:
            await asyncio.wait(
                self.application_futures.values(),
                return_when=asyncio.ALL_COMPLETED,
                timeout=self.application_close_timeout
            )
        except asyncio.TimeoutError:
            pass

    # Note if all child applications close within the timeout this cor-routine will be killed before we get here.

    async def websocket_send(self, message, stream_name):
        """
        Handle the sending of WebSocket messages with both textual and binary payloads.

        This method processes incoming WebSocket messages and routes them by decoding
        their payloads (either textual or binary) and packaging them into a dictionary
        along with the provided stream name. The processed data is then forwarded via
        a JSON-encoded response. In case of an unsupported message format (neither
        'text' nor 'bytes'), it raises a `ValueError`.

        :param message: Dict containing WebSocket message data, expected keys are "text" or "bytes".
        :param stream_name: Name of the stream associated with the incoming message.
        :raises ValueError: If the message does not contain "text" or "bytes".
        :returns: None
        """
        # Handle textual data
        if "text" in message:
            text = message.get("text")
            json = await self.decode_json(text)
            data = {
                "stream": stream_name,
                "payload": json
            }
            await self.send_json(data)
        # Handle binary data
        elif "bytes" in message:
            binary_data = message.get("bytes")
            # Transform or forward binary data as needed
            data = {
                "stream": stream_name,
                "payload": binary_data  # This assumes downstream accepts raw binary payloads
            }
            await self.send_json(data)

        else:
            raise ValueError("Invalid websocket message: Neither 'text' nor 'bytes' present.")

    async def websocket_accept(self, message, stream_name):
        """
        Intercept downstream `websocket.accept` message and thus allow this upsteam application to accept websocket
        frames.
        """
        is_first = not self.applications_accepting_frames
        self.applications_accepting_frames.add(stream_name)
        # accept the connection after the first upstream application accepts.
        if is_first:
            await self.accept()

    async def websocket_close(self, message, stream_name):
        """
        Handle downstream `websocket.close` message.

        Will disconnect this upstream application from receiving any new frames.

        If there are not more upstream applications accepting messages it will then call `close`.
        """
        if stream_name in self.applications_accepting_frames:
            # remove from set of upsteams steams than can receive new messages
            self.applications_accepting_frames.remove(stream_name)

        # we are already closing due to an upstream websocket.disconnect command

        if self.closing:
            return
        # if none of the upstream applications are listing we need to close.
        if not self.applications_accepting_frames:
            await self.close(message.get("code"))
