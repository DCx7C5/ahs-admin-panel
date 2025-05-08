import base64
import inspect
import json
import logging
import os
import shutil
import subprocess
from importlib import import_module

from time import sleep

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand
from django.utils import timezone
from docker import from_env, DockerClient

from django.apps import apps as django_apps
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)
logging.getLogger('docker.utils.config').setLevel(logging.INFO)



def parse_func_signature(func, exclude: list = None):
    """
    Parses the function signature to extract:
    - Positional arguments
    - Keyword arguments (with and without defaults)
    - Annotations
    """
    # Extract function signature
    sig = inspect.signature(func)
    args = []  # Positional arguments or ones with defaults
    kwargs = {}  # Keyword arguments (key: name, value: default)
    annotations = {}  # Parameter annotations
    exclude = exclude or []
    for name, param in sig.parameters.items():
        if name in exclude:
            continue
        # Capture annotations, if available
        if param.annotation != inspect.Parameter.empty:
            annotations[name] = param.annotation
        # Distinguish between positional arguments and kwargs with defaults
        if param.default == inspect.Parameter.empty:
            # No default means it's a positional argument
            args.append(name)
        else:
            # Has a default value
            kwargs[name] = param.default
    return args, kwargs, annotations

def clean_migrations_dirs(base_path, purge: bool = False):
    """
    Find all `migrations` directories under the given base path and delete all files
    in them except for `__init__.py`.

    :param base_path: Root directory to start searching from.
    :param purge: If True, deletes the migration directories; otherwise, cleans them.
    """
    for root, dirs, files in os.walk(base_path):
        # Filter for `migrations` directories
        if 'migrations' in dirs:
            migrations_dir = os.path.join(root, 'migrations')

            if purge:
                # Delete the entire migrations directory
                shutil.rmtree(migrations_dir)
                print(f"Purged directory: {migrations_dir}")
            else:
                # Only delete files in the migrations folder except `__init__.py`
                for file_name in os.listdir(migrations_dir):
                    file_path = os.path.join(migrations_dir, file_name)

                    # Keep `__init__.py`, delete everything else
                    if file_name != '__init__.py' and os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")


def get_all_apps():
    """
    Recursively find all directories containing a file named 'apps.py' starting from a specified path.
    :return: A list of directory paths containing 'apps.py'.
    """
    directories_with_apps_py = []
    for root, dirs, files in os.walk(settings.BASE_DIR / 'backend' ):
        if "apps.py" in files:  # Check if 'apps.py' exists in the current folder
            directories_with_apps_py.append(root.split('backend/')[-1].replace('/', '.'))
    if 'makemigrations' in directories_with_apps_py:
        directories_with_apps_py.remove('makemigrations')
    if 'modules' in directories_with_apps_py:
        directories_with_apps_py.remove('modules')
    if 'manage.py' in directories_with_apps_py:
        directories_with_apps_py.remove('manage.py')

    return directories_with_apps_py


def get_all_core_apps():
    """
    Returns a list of all core applications.

    This function filters all the applications obtained from the
    function `get_all_apps()` and returns only those whose names
    start with 'ahs' and do not end with 'models'.
    """
    return [x.split('.')[-1] for x in get_all_apps() if x.startswith('ahs') and not x.endswith('models')]

def get_all_plugin_apps():
    """
    Fetches all plugin applications from the available apps.

    This function iterates through all the applications retrieved from a different function
    and filters out non-plugin applications. Plugin applications are identified based
    on naming conventions, specifically by ensuring they do not start with 'ahs' and processing
    those that start with 'apps.'. The resulting list contains only plugin application names.
    """
    plugins = []
    for x in get_all_apps():
        if not x.startswith('ahs'):
            if x.startswith('apps.'):
                x = x.split('.')[-1]
            plugins.append(x)
    return plugins


class Docker:
    """
    Class providing utility methods for Docker container and service management.

    This class is designed to facilitate interaction with Docker containers and services
    using the Docker Python SDK. It provides methods for operations like starting, stopping,
    removing containers, managing Docker Compose services, handling Docker volumes,
    and closing the Docker client. The class aims to simplify common Docker operations
    with a reusable client for consistent and efficient resource management.

    Attributes:
        _cli: DockerClient | None
            Class-level attribute holding the instance of the Docker client.
        _print: Callable
            Function to handle output messages.
        _kwargs: dict
            Arguments for output messages, including properties like "end".

    Methods:
        get_client(cls, context= None):
            Retrieve and initialize a reusable client instance.

        wait_container_state(cls, name: str, timeout: int = 15, state: str = "running") -> bool:
            Waits for a container to reach a specific state within a given timeout.

        start_compose_service(cls, compose_file: str | os.PathLike, compose_project: str):
            Start and manage Docker Compose services for the application.

        start_container(cls, name: str):
            Starts a container with the given name and ensures it reaches the running state.

        stop_container(cls, name: str):
            Stops a running container by its name and ensures its state changes to "exited".

        remove_container(cls, name: str, with_vols: bool = False):
            Remove a specified container using its name.

        delete_volume(cls, name: str):
            Deletes a specified Docker volume by its name.

        close_client(cls):
            Closes the current client instance and resets it to a None value.
    """
    _cli: DockerClient | None = None
    _print = print
    _kwargs = {'end': '\r'}

    @classmethod
    def get_client(cls, context = None):
        """
        Retrieve and initialize a reusable client instance.

        This method retrieves a client instance if one already exists. If not, it
        initializes a new client from the environment. When a valid `context` object
        is provided, it will also set up context-specific configurations such as
        output redirection and additional arguments for printing.
        """
        if cls._cli is not None:
            return cls._cli
        cls._cli = from_env()
        if context is not None and isinstance(context, BaseCommand):
            cls._print = context.stdout.write
            cls._kwargs = {'ending': '\r'}
        return cls._cli

    @classmethod
    def wait_container_state(cls, name : str, timeout: int = 15, state: str = "running") -> bool:
        """
        Waits for a container to reach a specific state within a given timeout.

        This method continuously checks the state of a specified container and waits
        until it reaches the desired state. If the container does not reach the
        desired state within the defined timeout period, the method times out, logs
        an error, and returns False.

        Errors raised within the method will depend on exceptions from the container
        retrieval and status-checking mechanisms of the underlying environment.
        """
        container = cls._cli.containers.get(name)
        is_running = container.status == state
        start = timezone.now()
        delta_s = 0
        msg = f"Waiting for container {name} to reach {state} state..."
        cls._print(msg, **cls._kwargs)
        while not is_running:
            if delta_s >= timeout:
                logger.error(f"Container {name} did not reach {state} state in {timeout} seconds. Timing out.")
                return False
            cls._print(".", **cls._kwargs)
            delta_s = (timezone.now() - start).seconds
            sleep(1)
        return True

    @classmethod
    def start_compose_service(
            cls,
            compose_file=None,
            compose_project=None
    ):
        """
        Start and manage Docker Compose services for the application.

        This class method helps in starting Docker Compose services using a specified
        compose file and project name. It waits for the specified container to reach
        the target state and handles any errors that might occur during the process.
        """
        from django.conf import settings

        if compose_file is None:
            compose_file = settings.BASE_DIR / f"docker-compose{'-dev' if settings.DEBUG else ''}.yaml"

        if compose_project is None:
            compose_project = settings.PROJECT_NAME

        try:
            subprocess.run(["docker", "compose", "-f", f"{compose_file}", "-p", f"{compose_project}", "up", "-d"],
                           check=True)
            cls.wait_container_state(f"ahs_postgres", state="running")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: {e}")
        except subprocess.CalledProcessError as e:  # noqa
            raise subprocess.CalledProcessError(e.returncode, cmd=e.cmd)
        except Exception as e:
            raise Exception(f"An error occurred while starting Docker Compose services: {e}")

    @classmethod
    def stop_compose_service(
            cls,
            compose_file=None,
            compose_project=None
    ):
        from django.conf import settings

        if compose_file is None:
            compose_file = settings.BASE_DIR / f"docker-compose{'-dev' if settings.DEBUG else ''}.yaml"
        if compose_project is None:
            compose_project = settings.PROJECT_NAME

        try:
            subprocess.run(["docker", "compose", "-f", compose_file, "-p", compose_project, "stop"], check=True)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: {e}")
        except subprocess.CalledProcessError as e:  # noqa
            raise subprocess.CalledProcessError(e.returncode, cmd=e.cmd)
        except Exception as e:
            raise Exception(f"An error occurred while stopping Docker Compose services: {e}")

    @classmethod
    def remove_compose_service(
            cls,
            compose_file=None,
            compose_project=None
    ):
        """
        Remove Docker Compose services.

        Args:
            compose_file: Path to compose file, defaults to project docker-compose.yaml
            compose_project: Project name for Docker Compose
        """
        from django.conf import settings

        if compose_file is None:
            compose_file = settings.BASE_DIR / f"docker-compose{'-dev' if settings.DEBUG else ''}.yaml"

        if compose_project is None:
            compose_project = settings.PROJECT_NAME

        try:
            subprocess.run(["docker", "compose", "-f", compose_file, "-p", compose_project, "down"], check=True)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: {e}")
        except subprocess.CalledProcessError as e:  # noqa
            raise subprocess.CalledProcessError(e.returncode, cmd=e.cmd)
        except Exception as e:
            raise Exception(f"An error occurred while removing Docker Compose services: {e}")

    @classmethod
    def start_container(cls, name: str):
        """
        Starts a container with the given name and ensures it reaches the running state.

        This method interacts with the Docker client to retrieve a container by its name,
        starts the container, and waits until the container reaches the "running" state.
        """
        container = cls._cli.containers.get(name)
        container.start()
        cls.wait_container_state(name, state="running")

    @classmethod
    def stop_container(cls, name: str):
        """
        Stops a running container by its name and ensures its state changes to "exited".

        This method retrieves the specified container using its name, stops it, and
        waits until the container reaches the "exited" state. This is commonly used
        to halt operations of the container safely and synchronously.
        """
        container = cls._cli.containers.get(name)
        container.stop()
        cls.wait_container_state(name, state="exited")

    @classmethod
    def remove_container(cls, name: str, with_vols: bool = False):
        """
        Remove a specified container using its name.

        This class method allows the deletion of a container with the
        provided name using the Docker CLI client. Users can choose to
        remove associated volumes by setting the corresponding flag.
        """
        container = cls._cli.containers.get(name)
        container.remove(v=with_vols)

    @classmethod
    def delete_volume(cls, name: str):
        """
        Deletes a specified Docker volume by its name.

        This method interacts with the Docker API client to identify and remove
        a specific volume. It utilizes the Docker client's volume retrieval and
        removal functionality.
        """
        vol = cls._cli.volumes.get(name)
        vol.remove()

    @classmethod
    def close_client(cls):
        """
        Closes the current client instance and resets it to a None value.

        This class method ensures that the client instance (`_cli`) is
        properly closed and dereferenced, allowing for a clean shutdown
        of the client resource.
        """
        if cls._cli is not None:
            cls._cli.close()
            cls._cli = None


def encode_b64(data: str | bytes, safe: bool = False, encoding: str = 'utf-8') -> str:
    """
    Encodes the given bytes or string into a Base64 string, optionally URL-safe.

    Args:
        data (str | bytes): The input bytes or string to be encoded.
        safe (bool): If True, use URL-safe Base64 encoding (default: False).
        encoding (str): The encoding to use for strings (default: 'utf-8').

    Returns:
        str: The Base64 encoded string, URL-safe if specified.

    Raises:
        TypeError: If input is neither bytes nor string.
        UnicodeEncodeError: If string cannot be encoded with the specified encoding.
    """
    if isinstance(data, str):
        data = data.encode(encoding)
    elif not isinstance(data, bytes):
        raise TypeError("Input must be bytes or str")

    encoded = base64.b64encode(data).decode('ascii')
    if safe:
        encoded = encoded.replace('+', '-').replace('/', '_').rstrip('=')

    return encoded


async def aencode_b64(data: str | bytes, safe: bool = False, encoding: str = 'utf-8') -> str:
    """
    Asynchronously encode data using Base64 encoding, optionally URL-safe.
    """
    return await sync_to_async(encode_b64)(data, safe, encoding)


def decode_b64(base64_str: str, to_str: bool = False, encoding: str = 'utf-8') -> bytes | str:
    """
    Decodes a Base64 string into bytes or a string, handling standard or URL-safe encoding.

    Args:
        base64_str (str): The Base64 string to decode.
        to_str (bool): If True, return a string instead of bytes.
        encoding (str): The encoding to use for string output (default: 'utf-8').

    Returns:
        bytes | str: The decoded bytes or string.

    Raises:
        TypeError: If input is not a string.
        ValueError: If input is not a valid Base64 string.
        UnicodeDecodeError: If bytes cannot be decoded with the specified encoding.
    """
    if not isinstance(base64_str, str):
        raise TypeError("Input must be a string")

    padded = base64_str.replace('-', '+').replace('_', '/')
    padding_needed = (4 - len(padded) % 4) % 4
    padded += '=' * padding_needed

    try:
        decoded = base64.b64decode(padded)
        return decoded.decode(encoding) if to_str else decoded
    except Exception as e:
        raise ValueError("Failed to decode Base64 string") from e


async def adecode_b64(data: str, to_str: bool = False, encoding: str = 'utf-8') -> bytes | str:
    """
    Asynchronously decode a Base64 encoded string, optionally handling URL-safe encoding.
    """
    return await sync_to_async(decode_b64)(data, to_str, encoding)


def decode_json(data: str) -> dict:
    """
    Decode a JSON string into a Python dictionary.
    Args:
        data: The JSON string to decode.
    Returns:
        Decoded dictionary.
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}") from e


async def adecode_json(data: str) -> dict | str | int | bytes:
    """
    Asynchronously decode a JSON string into a Python dictionary.
    """
    return await sync_to_async(decode_json)(data)


def encode_json(obj) -> str:
    try:
        return json.dumps(obj)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON data: {e}") from e


async def aencode_json(obj) -> str:
    return await sync_to_async(encode_json)(obj)


def get_ahs_session_store():
    """
    Return the AHS session engine.
    """
    return import_module(settings.SESSION_ENGINE_AHS).AHSToken


def get_ahs_session_model():
    """
    Return the AHS session model.
    """

    try:
        return django_apps.get_model(
            settings.SESSION_MODEL_AHS,
            require_ready=False
        )
    except ValueError:
        raise ImproperlyConfigured(
            "SESSION_MODEL_AHS must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "SESSION_MODEL_AHS refers to model '%s' that has not been installed"
            % settings.AUTH_USER_MODEL
        )


def get_crypto_backend():
    try:
        crypto_cfg = settings.CRYPTO_BACKEND
        _cls = import_string(f'backend.ahs_core.{crypto_cfg.lower()}.{crypto_cfg.upper()}')
        return _cls()
    except AttributeError:
        raise ImproperlyConfigured("CRYPTO_BACKEND must be set")
