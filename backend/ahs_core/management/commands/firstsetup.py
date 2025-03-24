import stat
import os.path
import venv

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand

PROJECT_DIR = settings.BASE_DIR



def _create_socket_files():
    socket_dir = PROJECT_DIR / 'docker' / '.sockets'
    if socket_dir.exists():
        socket_dir.rmdir()

    socket_dir.mkdir(0o770)
    socket_dir.chmod(0o770)

    psql_socket_file = socket_dir / '.s.PGSQL.5432'
    psql_lock_file = socket_dir / '.s.PGSQL.5432.lock'
    redis_socket_file = socket_dir / 'redis.sock'
    socket_dir.chmod(0o770)

    if psql_lock_file.exists():
        psql_lock_file.unlink()

    if psql_socket_file.exists():
        psql_socket_file.unlink()

    if redis_socket_file.exists():
        redis_socket_file.unlink()

    os.mknod(psql_socket_file, mode=stat.S_IFSOCK)
    os.mknod(redis_socket_file, mode=stat.S_IFSOCK)
    os.chown(redis_socket_file,1000, 1000)
    os.chown(psql_socket_file,1000, 1000)
    os.chmod(redis_socket_file, 0o770)
    os.chmod(psql_socket_file, 0o770)


def create_venv_directory():
    venv_dir = PROJECT_DIR / '.venv'
    venv.create(venv_dir, with_pip=True)



class Command(BaseCommand):
    help = 'First setup AHS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            type=str,
            action='store',
            default='dev',
            help='Server environment (dev or prod). Default: dev',
        )


    def handle(self, *args, **options):
        call_command('migrate')
        call_command('loaddata', 'initial_data.json')
        env_param = options['env']
        if 'dev' in env_param.lower():
            dev_env = True
            prod_env = False
        elif 'prod' in env_param.lower():
            dev_env = False
            prod_env = True
        else:
            raise ImproperlyConfigured('Invalid environment parameter')

        if dev_env:
            self.stdout.write(self.style.SUCCESS('Setting up AHS development server...'))
            _create_socket_files()
        elif prod_env:
            self.stdout.write(self.style.SUCCESS('Setting up AHS production server...'))
