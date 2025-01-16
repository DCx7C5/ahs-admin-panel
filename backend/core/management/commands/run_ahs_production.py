
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Runs AHS Admin Panel in production mode"
    def add_arguments(self, parser):

        parser.add_argument(
            'hostname:port',
            action='store_true',
            dest='hostname',
            default=False,
            help='hostname:port',
        )

    def write(self, text):
        self.stdout.write(text)

    def write_error(self, text):
        self.stderr.write(text)

    def write_success(self, text):
        self.stdout.write(self.style.SUCCESS(text))

    def handle(self, *args, **options):
        self.write_success("Running AHS Admin Panel in Production mode")
