import logging
import os
from typing import Tuple, Dict

from daphne.management.commands.runserver import get_default_application
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.management import BaseCommand
from docker import client
from django.core.management.commands.runserver import Command as DjangoRunserverCommand

from config.settings import BASE_DIR

docker_client = client.from_env()
User = get_user_model()

# Make sure we have a logger
logger = logging.getLogger("django.channels.server")


class Command(BaseCommand):
    help = "Runs AHS Admin Panel and is kind of an entrypoint script at for the docker environment"

    default_environment = 'development'

    default_addr = "127.0.0.1"
    default_addr_ipv6 = "::1"
    default_port = "8000"
    protocol = "http"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._address = None
        self._docker_client = docker_client
        self._mode = "development"

        self._docker: Dict[str, Dict | None] = {
            'postgres': {'name': 'ahs_postgres', 'is_running': False, 'socket': None},
            'redis': {'name': 'ahs_redis', 'is_running': False, 'socket': None},
            'node': {'name': 'ahs_node', 'is_running': False},
        }

    def add_arguments(self, parser):
        parser.add_argument(
            'option',
            nargs='?',
        )

    def collect_info(self):
        containers = self._docker_client.containers()
        for container in containers:
            for db in ['postgres', 'redis']:
                if f'/ahs_{db}' in container['Names']:
                    self._docker[db] = {
                        'is_running': container['State'] == 'running',
                        'ip_address': container['NetworkSettings']['Networks']['admin-panel_default']['IPAddress'],
                        'port': container['Ports'][0]['PublicPort'],
                    }
                    for mount in container['Mounts']:
                        if mount['Type'] == 'bind' and mount['Source'].endswith("/docker/postgres"):
                            self._docker[db]['socket'] = mount['Source']
                        elif mount['Type'] == 'bind' and mount['Source'].endswith("/docker/redis"):
                            self._docker[db]['socket'] = mount['Source']

            if '/ahs_node' in container['Names']:
                self._docker['node'] = {
                    'is_running': container['State'] == 'running',
                    'ip_address': container['NetworkSettings']['Networks']['admin-panel_default']['IPAddress'],
                }


    def print_info(self):
        self.write_success("AHS Admin Panel Entrypoint:")
        self.write('===========================')
        self.write('')
        self.write_success("Mode: ", end='')
        self.write(self._mode)
        self.write_success("Serving: ", end='')
        self.write(f"{self._address[0]}:{self._address[1]}")

        if self._docker['postgres']['is_running']:
            self.stdout.write(self.style.SUCCESS('PostgreSQL: ') + self.style.SUCCESS('running'))
            self.write(
                f"Address: {self._docker['postgres']['ip_address']}:{self._docker['postgres']['port']}"
            )
            self.write(f"Socket Mount: {self._docker['postgres']['socket']}")
        else:
            self.stdout.write(self.style.SUCCESS('PostgreSQL: ') + self.style.ERROR('not running'))

        if self._docker['redis']['is_running']:
            self.stdout.write(self.style.SUCCESS('Redis: ') + self.style.SUCCESS('running'))
            self.write(
                f"Address: {self._docker['redis']['ip_address']}:{self._docker['redis']['port']}"
            )
            self.write(f"Socket Mount: {self._docker['redis']['socket']}")
        else:
            self.stdout.write(self.style.SUCCESS('Redis: ') + self.style.ERROR('not running'))

        if self._docker['node']['is_running']:
            self.stdout.write(self.style.SUCCESS('Node: ') + self.style.SUCCESS('running'))
        else:
            self.stdout.write(self.style.SUCCESS('Node: ') + self.style.ERROR('not running'))

        if (not self._docker['postgres']['is_running']
                or not self._docker['redis']['is_running']
                or not self._docker['node']['is_running']
        ):
            self.write('')
            self.write_error("Please start the required services before starting AHS Admin Panel")
            start = input('Do you want to start the containers? (Y/n): ')
            if start.lower() == 'y' or start == '':
                self._start_container()
            else:
                exit(1)

    def overwrite_env_vars(self):
        """Overwrite env vars for socket access over docker mounts"""
        os.environ['DB_HOST'] = self._docker['postgres']['socket']
        os.environ['REDIS_HOST'] = 'system://' + self._docker['redis']['socket'] + '/redis.sock'

    def save_new_socket_addresses_in_env_file(self):
        ow = input('Do you want to overwrite the sockets in your env file? (Y/n):')
        if ow.lower() == 'y' or ow == '':
            with open('.env', 'r') as f:
                lines = f.readlines()
            for line in lines:
                if line.startswith('DB_HOST'):
                    lines[lines.index(line)] = f"DB_HOST={self._docker['postgres']['socket']}\n"
                elif line.startswith('REDIS_HOST'):
                    lines[lines.index(line)] = f"REDIS_HOST=system://{self._docker['redis']['socket']}/redis.sock\n"
            with open('.env', 'w') as f:
                f.writelines(lines)

    def _start_container(self):
        for container in self._docker:
            if not self._docker[container]['is_running']:
                self._docker_client.start(self._docker[container]['name'])

    def write(self, text, end="\n"):
        self.stdout.write(text, ending=end)

    def write_error(self, text, end="\n"):
        self.stderr.write(text, ending=end)

    def write_success(self, text, end="\n"):
        self.stdout.write(self.style.SUCCESS(text), ending=end)

    def handle(self, *args, **kwargs):

        hostname = kwargs.get('hostname', '0.0.0.0')
        port = kwargs.get('port', '8000')
        self._address = (hostname, port)
        self.collect_info()
        self.print_info()

    def get_application(self, options):
        """
        Returns the static files serving application wrapping the default application,
        if static files should be served. Otherwise just returns the default
        handler.
        """
        staticfiles_installed = apps.is_installed("django.contrib.staticfiles")
        use_static_handler = options.get("use_static_handler", staticfiles_installed)
        insecure_serving = options.get("insecure_serving", False)
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return ASGIStaticFilesHandler(get_default_application())
        else:
            return get_default_application()

    def log_action(self, protocol, action, details):
        """
        Logs various different kinds of requests to the console.
        """
        # HTTP requests
        if protocol == "http" and action == "complete":
            msg = "HTTP %(method)s %(path)s %(status)s [%(time_taken).2f, %(client)s]"

            # Utilize terminal colors, if available
            if 200 <= details["status"] < 300:
                # Put 2XX first, since it should be the common case
                logger.info(self.style.HTTP_SUCCESS(msg), details)
            elif 100 <= details["status"] < 200:
                logger.info(self.style.HTTP_INFO(msg), details)
            elif details["status"] == 304:
                logger.info(self.style.HTTP_NOT_MODIFIED(msg), details)
            elif 300 <= details["status"] < 400:
                logger.info(self.style.HTTP_REDIRECT(msg), details)
            elif details["status"] == 404:
                logger.warning(self.style.HTTP_NOT_FOUND(msg), details)
            elif 400 <= details["status"] < 500:
                logger.warning(self.style.HTTP_BAD_REQUEST(msg), details)
            else:
                # Any 5XX, or any other response
                logger.error(self.style.HTTP_SERVER_ERROR(msg), details)

        # Websocket requests
        elif protocol == "websocket" and action == "connected":
            logger.info("WebSocket CONNECT %(path)s [%(client)s]", details)
        elif protocol == "websocket" and action == "disconnected":
            logger.info("WebSocket DISCONNECT %(path)s [%(client)s]", details)
        elif protocol == "websocket" and action == "connecting":
            logger.info("WebSocket HANDSHAKING %(path)s [%(client)s]", details)
        elif protocol == "websocket" and action == "rejected":
            logger.info("WebSocket REJECT %(path)s [%(client)s]", details)
