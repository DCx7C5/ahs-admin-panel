import logging
import os
from time import sleep

from django.core.management import BaseCommand, CommandError
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand

from config.settings import BASE_DIR
from .populateall import Command as PopulateCommand
from ...utils import Docker

logger = logging.getLogger(__name__)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)


def clean_migrations_dirs():
    """
    Find all `migrations` directories under the given base path and delete all files
    in them except for `__init__.py`.
    """
    for root, dirs, files in os.walk(BASE_DIR / 'backend'):
        # Filter for `migrations` directories
        if 'migrations' in dirs:
            migrations_dir = os.path.join(root, 'migrations')

            for file_name in os.listdir(migrations_dir):
                file_path = os.path.join(migrations_dir, file_name)

                # Keep `__init__.py`, delete everything else
                if file_name != '__init__.py' and os.path.isfile(file_path):
                    os.remove(file_path)


class Command(BaseCommand):
    help = "Delete migration directory contents"

    def add_arguments(self, parser):
        parser.add_argument(
            "--purge",
            action='store_true',
            default=False,
            help="Deletes the docker postgres database volume",
        )

        parser.add_argument(
            '--migrate',
            action='store_true',
            default=False,
            help="Migrate database after deleting migrations",
        )

        parser.add_argument(
            "--populate",
            action='store_true',
            default=False,
            help="Populate database after deleting migrations",
        )

    def handle(self, *args, **options):
        try:
            if options['purge']:
                Docker.get_client(context=self)
                self.stdout.write('Deleting docker database volume...')
                Docker.stop_container("ahs_postgres")
                Docker.remove_container("ahs_postgres", with_vols=True)
                self.stdout.write(self.style.SUCCESS('Deleting docker database volume... Done'))
                self.stdout.write('Restarting docker services...')
                Docker.start_compose_service()
                self.stdout.write(self.style.SUCCESS('Restarting docker services... Done'))
            self.stdout.write('Cleaning migration directory contents...')
            clean_migrations_dirs()
            self.stdout.write(self.style.SUCCESS('Cleaning migration directory contents... Done'))
            if options['migrate']:
                sleep(3)
                self.stdout.write('Migrating database...')
                MakeMigrationsCommand().run_from_argv(['manage.py', 'makemigrations'])
                self.stdout.write(self.style.SUCCESS('Making migrations... Done'))
                MigrateCommand().run_from_argv(['manage.py', 'migrate'])
                self.stdout.write(self.style.SUCCESS('Migrating database... Done'))
            if options['populate']:
                PopulateCommand().handle()

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        finally:
            Docker.close_client()
