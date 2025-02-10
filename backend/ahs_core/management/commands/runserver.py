import errno
import logging
import os
import shutil
import sys
from datetime import datetime
from typing import Tuple, Dict

from channels.routing import get_default_application
from daphne.endpoints import build_endpoint_description_strings
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.utils import autoreload
from docker import APIClient


from django.core.management import BaseCommand
from django.core.management.commands.runserver import Command as DjangoRunserverCommand
from daphne.management.commands.runserver import RunserverCommand as DaphneRunserverCommand
from hypercorn.trio.tcp_server import TCPServer


docker_client = APIClient()
AHSUser = get_user_model()

# Make sure we have a logger
logger = logging.getLogger("django.channels.server")




def delete_dirs_with_name(base_dir, target_dir_name):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for dir_name in dirs:
            if dir_name == target_dir_name:
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)


def get_or_create_superuser() -> Tuple[str, str]:
    try:
        admin = AHSUser.objects.filter(is_superuser=True).first()
    except AHSUser.DoesNotExist:
        admin = None




class Command(DjangoRunserverCommand):
    help = "Runs AHS Admin Panel and is kind of an entrypoint script for the docker environment"

    requires_system_checks = []
    stealth_options = ("shutdown_message",)
    suppressed_base_arguments = {"--verbosity", "--traceback"}

    default_environment = 'development'

    default_addr = "127.0.0.1"
    default_addr_ipv6 = "::1"
    default_port = "8000"
    protocol = "http"
    server_cls = ASGIServer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol = None
        self._docker_client = APIClient()
        self._mode = "development"
        self._address: Tuple[str, str | int] | None = None
        self._docker: Dict[str, Dict | None] = {
            'postgres': {'name': 'ahs_postgres', 'is_running': False, 'socket': None},
            'redis': {'name': 'ahs_redis', 'is_running': False, 'socket': None},
            'node': {'name': 'ahs_node', 'is_running': False},
        }

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport", nargs="?", help="Optional port number, or ipaddr:port"
        )

        parser.add_argument(
            "--noasgi",
            action="store_false",
            dest="use_asgi",
            default=True,
            help="Run the old WSGI-based runserver rather than the ASGI-based one",
        )

        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Tells Django to NOT use the auto-reloader.",
        )

        parser.add_argument(
            '--docker',
            action='store_true',
            type=bool,
            dest='docker',
            default=True,
            help='Run AHS Admin Panel in docker environment',
        )
        parser.add_argument(
            '--purge',
            action='store_true',
            dest='purge',
            type=bool,
            default=False,
            help='Purge all docker containers, volumes, migration dirs',
        )
        parser.add_argument(
            "--ipv6",
            "-6",
            action="store_true",
            dest="use_ipv6",
            help="Tells Django to use an IPv6 address.",
        )
        parser.add_argument(
            "-w",
            "--ahs_workers",
            dest="ahs_workers",
            help="The number of ahs_workers to spawn and use",
            type=int,
        )
        setattr(parser, 'use_threading', True)


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
        if kwargs.get('purge', ''):
            pass


        hostname = kwargs['hostname']
        port = kwargs['port']
        self._address = (hostname, port)
        self.collect_info()
        self.print_info()

        self.http_timeout = options.get("http_timeout", None)
        self.websocket_handshake_timeout = options.get("websocket_handshake_timeout", 5)
        # Check Channels is installed right
        if options["use_asgi"] and not hasattr(settings, "ASGI_APPLICATION"):
            raise CommandError(
                "You have not set ASGI_APPLICATION, which is needed to run the server."
            )
        # Dispatch upward
        super().handle(*args, **options)

    def inner_run(self, *args, **options):
        # Maybe they want the wsgi one?
        if not options.get("use_asgi", True):
            if hasattr(RunserverCommand, "server_cls"):
                self.server_cls = RunserverCommand.server_cls
            return RunserverCommand.inner_run(self, *args, **options)
        # Run checks
        self.stdout.write("Performing system checks...\n\n")
        self.check(display_num_errors=True)
        self.check_migrations()
        # Print helpful text
        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"
        now = datetime.datetime.now().strftime("%B %d, %Y - %X")
        self.stdout.write(now)
        self.stdout.write(
            (
                "Django version %(version)s, using ahs_settings %(ahs_settings)r\n"
                "Starting ASGI/Daphne version %(daphne_version)s development server"
                " at %(protocol)s://%(addr)s:%(port)s/\n"
                "Quit the server with %(quit_command)s.\n"
            )
            % {
                "version": self.get_version(),
                "server": __version__,
                "ahs_settings": settings.SETTINGS_MODULE,
                "protocol": self.protocol,
                "addr": "[%s]" % self.addr if self._raw_ipv6 else self.addr,
                "port": self.port,
                "quit_command": quit_command,
            }
        )

        # Launch server in 'main' thread. Signals are disabled as it's still
        # actually a subthread under the autoreloader.
        logger.debug("Daphne running, listening on %s:%s", self.addr, self.port)

        # build the ahs_endpoints description string from host/port options
        endpoints = build_endpoint_description_strings(host=self.addr, port=self.port)
        try:
            self.server_cls(
                application=self.get_application(options),
                endpoints=endpoints,
                signal_handlers=not options["use_reloader"],
                action_logger=self.log_action,
                http_timeout=self.http_timeout,
                root_path=getattr(settings, "FORCE_SCRIPT_NAME", "") or "",
                websocket_handshake_timeout=self.websocket_handshake_timeout,
            ).run()
            logger.debug("Daphne exited")
        except KeyboardInterrupt:
            shutdown_message = options.get("shutdown_message", "")
            if shutdown_message:
                self.stdout.write(shutdown_message)
            return

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
        """Logs various different kinds of requests to the console."""

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
