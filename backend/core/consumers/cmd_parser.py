import inspect
import json
import logging
from functools import wraps
from typing import (
    Dict,
    Callable,
    Coroutine,
    AsyncGenerator, Set, List,
)

from django.contrib.auth import get_user_model

from config import settings
from backend.core.utils import parse_func_signature

logging.getLogger('daphne.ws_protocol').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

AHSUser = get_user_model()


class CmdMapper:
    apps: Set[str] = {app.split(".")[1] for app in settings.INSTALLED_APPS if app.startswith('backend')}

    def __init__(self):
        self.callbacks: Dict[str, str | List | Dict | None] = {}

    def register_callback(self, app: str, func_name: str, func: Callable[..., Coroutine] | AsyncGenerator):
        if app not in self.apps:
            raise ValueError(f"App '{app}' not found in registered apps.")
        if func_name not in self.callbacks.keys():
            self.callbacks[func_name] = {'args': [],'kwargs': {},'annotations': {},'func': None}
        (self.callbacks[func_name]['args'],
             self.callbacks[func_name]['kwargs'],
             self.callbacks[func_name]['annotations']) = (parse_func_signature(func, ['user']))
        self.callbacks[func_name]['func'] = func
        logger.debug(f"Registered callback '{func_name}' for app '{app}' with function {func}")




class CmdHandler:

    commands: Dict[str, Dict[str, Dict[str,Callable[..., Coroutine]]]] = {}

    def __init__(self):
        self.commands: Dict[str, Dict[str, Dict[str,Callable[..., Coroutine]]]] = {}

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


CommandMapper = CmdMapper()


def websocket_cmd(func):
    """Decorator to register a WebSocket command dynamically with CmdParser."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    # Dynamically retrieve the app name and command name
    app_name = func.__module__.split('.')[1]
    func_name = func.__name__  # Extract function name

    CommandMapper.register_callback(app_name, func_name, func)
    logger.debug(f"Registered callback '{func_name}' for app '{app_name}' with function {func}")
    return wrapper
