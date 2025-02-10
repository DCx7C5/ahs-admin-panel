import logging
import os
from time import sleep

from django.core.management import BaseCommand, CommandError
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand

from config.settings import BASE_DIR, DEBUG
from .populate import Command as PopulateCommand
import docker

logger = logging.getLogger(__name__)
logging.getLogger('docker.utils.config').setLevel(logging.INFO)

docker_client = docker.from_env()


def start_service_from_compose():
    try:
        # Initialize the Docker client
        client = docker.from_env()
        compose_project = "ahs-admin-panel"
        compose_file = BASE_DIR / f"docker-compose{'-dev' if DEBUG else ''}.yaml"


        # Run the docker-compose up command (using a subprocess call to docker-compose)
        # Docker-py does not directly support Docker Compose deployments out of the box.
        import subprocess
        subprocess.run(["docker", "compose", "-f", f"{compose_file}", "-p", f"{compose_project}", "up", "-d"], check=True)

        print(f"Docker Compose services started successfully for project: {compose_project}.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start services from compose file. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def stop_database_container():
    container = docker_client.containers.get('ahs_postgres')
    container.stop()
    container.remove()


def delete_docker_database_volume():
    stop_database_container()
    vol = docker_client.volumes.get('ahs-admin-panel_postgres-data')
    vol.remove()


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
                    print(f"Deleted: {file_path}")



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
                self.stdout.write(self.style.SUCCESS('Deleting docker database volume...'))
                delete_docker_database_volume()
                self.stdout.write(self.style.SUCCESS('Deleting docker database volume... Done'))
                self.stdout.write(self.style.SUCCESS('Restarting docker services...'))
                start_service_from_compose()
                self.stdout.write(self.style.SUCCESS('Restarting docker services... Done'))
            else:
                self.stdout.write(self.style.SUCCESS('Cleaning migration directory contents...'))
                clean_migrations_dirs()
                self.stdout.write(self.style.SUCCESS('Cleaning migration directory contents... Done'))
            if options['migrate']:
                sleep(10)
                self.stdout.write(self.style.SUCCESS('Migrating database...'))
                MakeMigrationsCommand().run_from_argv(['manage.py', 'makemigrations'])
                self.stdout.write(self.style.SUCCESS('Making migrations... Done'))
                MigrateCommand().run_from_argv(['manage.py', 'migrate'])
                self.stdout.write(self.style.SUCCESS('Migrating database... Done'))
            if options['populate']:
                PopulateCommand().handle()

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        finally:
            docker_client.close()

