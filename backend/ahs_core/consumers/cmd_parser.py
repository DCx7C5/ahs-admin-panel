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
from backend.ahs_core.utils import parse_func_signature

logging.getLogger('daphne.ws_protocol').setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
User = get_user_model()


class CmdMapper:
    """
    Manages mapping of callback functions to specific applications within the project.

    The CmdMapper class is responsible for managing and registering callback functions
    associated with different apps in the project. It validates and ensures that a
    callback function is correctly registered under its corresponding app, and also
    parses the function's signature for arguments, keyword arguments, and annotations.
    This functionality is particularly useful when working in an asynchronous environment,
    allowing developers to easily map and handle callbacks.

    Attributes:
        apps (Set[str]): A set of applications derived from the installed applications
        in the project's ahs_settings where each app begins with "backend".
        callbacks (Dict[str, Union[str, List, Dict, None]]): A dictionary where each
        key is the callback function name, and the value stores the parsed signature
        (args, kwargs, annotations) and the function itself.

    Methods:
        register_callback(app: str, func_name: str, func: Callable[..., Coroutine] | AsyncGenerator):
            Registers a callback function for a specified app and stores its signature
            details. Throws a ValueError if the app is not found in the registered
            `apps` set.
    """
    apps: Set[str] = {
        app.split(".")[1]
        for app in settings.INSTALLED_APPS
        if app.startswith('backend') and "." in app
    }
    def __init__(self):
        self.callbacks: Dict[str, str | List | Dict | None] = {}

    def register_django_callback(self, app: str, func_name: str, func: Callable[..., Coroutine] | AsyncGenerator):
        if app not in self.apps:
            raise ValueError(f"App '{app}' not found in registered apps.")
        if func_name not in self.callbacks.keys():
            self.callbacks[func_name] = {'args': [],'kwargs': {},'annotations': {},'func': None}
        (self.callbacks[func_name]['args'],
             self.callbacks[func_name]['kwargs'],
             self.callbacks[func_name]['annotations']) = (parse_func_signature(func, ['user']))
        self.callbacks[func_name]['func'] = func
        logger.debug(f"Registered callback '{func_name}' for app '{app}' with function {func}")





CommandMapper = CmdMapper()


def websocket_cmd(func):
    """Decorator to register a WebSocket command dynamically with CmdParser."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    # Dynamically retrieve the app name and command name
    app_name = func.__module__.split('.')[1]
    func_name = func.__name__  # Extract function name

    CommandMapper.register_django_callback(app_name, func_name, func)
    logger.debug(f"Registered callback '{func_name}' for app '{app_name}' with function {func}")
    return wrapper
