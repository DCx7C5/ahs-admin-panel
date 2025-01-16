from dataclasses import dataclass
import inspect
import json
import logging
from uuid import UUID
from functools import wraps
from typing import (
    List,
    Dict,
    Callable,
    Coroutine,
    AsyncGenerator,
)

from django.contrib.auth import get_user_model

from config import settings

logging.getLogger('daphne.ws_protocol').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

AHSUser = get_user_model()


CommandDictionary = {
    app: {

    } for app in settings.INSTALLED_APPS
}



@dataclass
class Command:
    """Dataclass representing a command/message."""

    __slots__ = ('app', 'func_name', 'func_args', 'func_kwargs',
                 'owner', 'send_resp_coro', 'unique_call_id', 'cb')

    app: str
    func_name: str
    func_args: List[any]
    func_kwargs: List[Dict[str, any]]
    owner: int | str | AHSUser
    send_resp_coro: Callable[..., Coroutine]
    unique_call_id: str | UUID | int
    cb: Callable[..., Coroutine] | AsyncGenerator | None

    def __post_init__(self):
        if not self.cb:
            ...

    @staticmethod
    def validate_params(params: List[str], required_params: List[str]) -> bool:
        """Validates if the required parameters are included in the inputs."""
        missing_params = [p for p in required_params if p not in params]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")
        return True



class CmdHandler:

    commands: Dict[str, Dict[str, Dict[str,Callable[..., Coroutine]]]] = {}

    def __init__(self):
        self.commands: Dict[str, Dict[str, Dict[str,Callable[..., Coroutine]]]] = {}

    def register_function(self, app: str, cmd: str, func: Callable[..., Coroutine]):
        """Register a function for an app and command name."""
        if app not in self.commands:
            self.commands[app] = {}
        kwargs = dict(inspect.signature(func).parameters)
        self.commands[app][cmd] = {'func': func, 'kwargs': kwargs}
        logger.debug(f"Registered command '{cmd}:{kwargs}' for app '{app}' with function {func}")

    async def __call__(self, data, user: AHSUser, send_coro: Callable[..., Coroutine]):
        """Handle a command by parsing and executing it."""
        try:
            app = data.pop('app', None)
            command = data.pop('cmd', None)
            kwargs = data.pop('kwargs', None)
            unique_id = data.pop('uniqueId', None)
            logger.debug(f"Received command: {app},{command},{kwargs},{unique_id}")
            if not app or not command:
                logger.warning("App or command missing in the received input.")
                return

            if app not in self.commands or command not in self.commands[app]:
                logger.warning(f"Command '{command}' for app '{app}' not found.")
                return
            func = self.commands[app][command]['func']
            await self.execute(func, user, send_coro, app, command, unique_id, **kwargs)
            logger.debug(f"Command '{command}' for app '{app}' executed successfully.{kwargs}")
        except Exception as e:
            logger.exception(f"Error while executing command: {e}")

    async def execute(self, func, user: AHSUser, send_coro: Callable[..., Coroutine], app: str, cmd: str, unique_id = None, **kwargs):
        logger.debug(f"Executing command '{cmd}' for app '{app}' with kwargs: {kwargs}")

        func_params = self.commands[app][cmd]['kwargs']

        # Define required parameters from the function signature
        required_params = {key for key, param in func_params.items() if param.default == param.empty and key != 'user'}

        # Extract valid kwargs for the function being called
        valid_kwargs = {key: value for key, value in kwargs.items() if key in func_params}

        # Check for missing required arguments
        missing_params = required_params - valid_kwargs.keys()
        if missing_params:
            raise ValueError(
                f"Missing required parameters for command '{cmd}' in app '{app}': {missing_params}"
            )

        try:
            # Check if the function is an async generator
            is_async_generator = inspect.isasyncgenfunction(func)

            if is_async_generator:
                logger.debug(f"Executing async generator function '{func.__name__}' for command '{cmd}'")
                # Call the function and send each yielded result
                async for data in func(user, **valid_kwargs):
                    await send_coro(
                        json.dumps({
                            'app': app,
                            'cmd': cmd,
                            'data': data,
                            'uniqueId': unique_id
                        })
                    )
            else:
                logger.debug(f"Executing regular async function '{func.__name__}' for command '{cmd}'")
                # Call the function and send the single result
                result = await func(user, **valid_kwargs)
                if result is not None:
                    await send_coro(
                        json.dumps({
                            'app': app,
                            'cmd': cmd,
                            'data': result,
                            'uniqueId': unique_id
                        })
                    )

        except Exception as e:
            logger.exception(f"Error while executing command '{cmd}': {e}")


CmdHandlerIns = CmdHandler()



def websocket_cmd(func):
    """Decorator to register a WebSocket command dynamically with CmdParser."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    # Dynamically retrieve the app name and command name
    module_path = func.__module__  # e.g., 'backend.bookmarks.commands'
    app = module_path.split('.')[1] if module_path.startswith('backend') else module_path.split('.')[0]
    func_name = func.__name__  # Extract function name

    # Register the function in CmdParser
    CmdHandlerIns.register_function(app, func_name, func)

    return wrapper

