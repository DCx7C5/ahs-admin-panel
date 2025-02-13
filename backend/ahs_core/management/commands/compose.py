import logging
from time import sleep

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from backend.ahs_core.utils import Docker

logger = logging.getLogger(__name__)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('docker.utils.config').setLevel(logging.INFO)


class Command(BaseCommand):
    help = "Control docker compose service"
    client = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--start",
            action='store_true',
            default=False,
        )

        parser.add_argument(
            "--stop",
            action='store_true',
            default=False,
        )

        parser.add_argument(
            "--restart",
            action='store_true',
            default=False,
        )
        parser.add_argument(
            "--remove",
            action='store_true',
            default=False,
        )


    def handle(self, *args, **options):
        self.client = Docker.get_client(context=self)
        try:
            if not options['start'] and not options['stop'] and not options['restart'] and not options['remove']:
                raise CommandError("You must specify one of --start, --stop, --restart, --remove")

            if options['start']:
                self.stdout.write(f"Starting docker service: {settings.PROJECT_NAME}")
                Docker.start_compose_service()
                self.stdout.write(self.style.SUCCESS('Starting docker service... Done'))
            elif options['stop']:
                self.stdout.write(f"Stopping docker service: {settings.PROJECT_NAME}")
                Docker.stop_compose_service()
                self.stdout.write(self.style.SUCCESS('Stopping docker service... Done'))
            elif options['restart']:
                self.stdout.write(f"Restarting docker service: {settings.PROJECT_NAME}")
                Docker.stop_compose_service()
                sleep(5)
                Docker.start_compose_service()
                self.stdout.write(self.style.SUCCESS('Restarting docker service... Done'))
            elif options['remove']:
                self.stdout.write(f"Removing docker service: {settings.PROJECT_NAME}")
                Docker.remove_compose_service()
                self.stdout.write(self.style.SUCCESS('Removing docker service... Done'))
        finally:
            Docker.close_client()
