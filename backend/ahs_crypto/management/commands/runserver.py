import datetime
import importlib
import logging
import os
import sys
from getpass import getpass

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.exceptions import ImproperlyConfigured
from django.core.management import CommandError
from django.core.management.commands.runserver import Command as RunserverCommand

from daphne import __version__
from daphne.endpoints import build_endpoint_description_strings
from daphne.server import Server

from backend.ahs_crypto.ecc import derive_from_private_root_key

logger = logging.getLogger("django.channels.server")


def get_default_application():
    """
    Gets the default application, set in the ASGI_APPLICATION setting.
    """
    try:
        path, name = settings.ASGI_APPLICATION.rsplit(".", 1)
    except (ValueError, AttributeError):
        raise ImproperlyConfigured("Cannot find ASGI_APPLICATION setting.")
    try:
        module = importlib.import_module(path)
    except ImportError:
        raise ImproperlyConfigured("Cannot import ASGI_APPLICATION module %r" % path)
    try:
        value = getattr(module, name)
    except AttributeError:
        raise ImproperlyConfigured(
            f"Cannot find {name!r} in ASGI_APPLICATION module {path}"
        )
    return value


class Command(RunserverCommand):
    protocol = "http"
    server_cls = Server
    _temp_marker_file = None  # Temporary marker file for session

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--noasgi",
            action="store_false",
            dest="use_asgi",
            default=True,
            help="Run the old WSGI-based runserver rather than the ASGI-based one",
        )
        parser.add_argument(
            "--http_timeout",
            action="store",
            dest="http_timeout",
            type=int,
            default=None,
            help=(
                "Specify the daphne http_timeout interval in seconds "
                "(default: no timeout)"
            ),
        )
        parser.add_argument(
            "--websocket_handshake_timeout",
            action="store",
            dest="websocket_handshake_timeout",
            type=int,
            default=5,
            help=(
                "Specify the daphne websocket_handshake_timeout interval in "
                "seconds (default: 5)"
            ),
        )

    def handle(self, *args, **options):
        try:
            if not self.session_marker_exists():
                green = self.style.SUCCESS
                password = getpass("Enter Root PrivateKey password:\n" + green('>>> '))
                privroot = derive_from_private_root_key(password)
                pubroot = privroot.public_key()
                settings.SIMPLE_JWT['SIGNING_KEY'] = privroot
                settings.SIMPLE_JWT['VERIFYING_KEY'] = pubroot
                self.stdout.write(green('Signingkey derived successfully.'))

                # Create a temporary marker file to skip password on reload
                self.create_session_marker()

            self.http_timeout = options.get("http_timeout", None)
            self.websocket_handshake_timeout = options.get("websocket_handshake_timeout", 5)

            # Django channels ASGI validation
            if options["use_asgi"] and not hasattr(settings, "ASGI_APPLICATION"):
                raise CommandError(
                    "You have not set ASGI_APPLICATION, which is needed to run the server."
                )

            # Call parent handler
            super().handle(*args, **options)
        except KeyboardInterrupt:
            pass
        finally:
            if self.session_marker_exists():
                self.remove_session_marker()
                self.stdout.write("Session marker removed. Runserver password prompt will occur next time.")

    def session_marker_exists(self):
        self._temp_marker_file = os.path.join(".runserverahs_session")
        return os.path.exists(self._temp_marker_file)

    def create_session_marker(self):
        if not self._temp_marker_file:
            self._temp_marker_file = os.path.join(".runserverahs_session")
        with open(self._temp_marker_file, "w") as marker:
            marker.write("1")  # Write a simple flag to indicate the marker exists

    def remove_session_marker(self):
        try:
            if self._temp_marker_file and os.path.exists(self._temp_marker_file):
                os.remove(self._temp_marker_file)
        except Exception as e:
            # Log cleanup errors, but don't raise exceptions that halt execution
            logger.warning(f"Failed to clean up session marker: {e}")

    def inner_run(self, *args, **options):
        try:
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
                    "Django version %(version)s, using settings %(settings)r\n"
                    "Starting AHS ADMIN ASGI/Daphne version %(daphne_version)s development server"
                    " at %(protocol)s://%(addr)s:%(port)s/\n"
                    "Quit the server with %(quit_command)s.\n"
                )
                % {
                    "version": self.get_version(),
                    "daphne_version": __version__,
                    "settings": settings.SETTINGS_MODULE,
                    "protocol": self.protocol,
                    "addr": "[%s]" % self.addr if self._raw_ipv6 else self.addr,
                    "port": self.port,
                    "quit_command": quit_command,
                }
            )

            # Launch server in 'main' thread. Signals are disabled as it's still
            # actually a subthread under the autoreloader.
            logger.debug("Daphne running, listening on %s:%s", self.addr, self.port)

            # Build the endpoint description string from host/port options
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
        finally:
            # Always cleanup the marker file upon process end
            self.remove_session_marker()

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
