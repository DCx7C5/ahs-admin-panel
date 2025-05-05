import stat
import os.path
import venv
import subprocess

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand

PROJECT_DIR = settings.BASE_DIR
SOCKET_DIR = PROJECT_DIR / 'docker' / '.sockets'
PSQL_SOCKET_FILE = SOCKET_DIR / '.s.PGSQL.5432'
PSQL_LOCK_FILE = SOCKET_DIR / '.s.PGSQL.5432.lock'
REDIS_SOCKET_FILE = SOCKET_DIR / 'redis.sock'


def _create_socket_files():
    if not os.path.exists(SOCKET_DIR):
        SOCKET_DIR.mkdir(0o770)
    os.chmod(SOCKET_DIR, 0o770)

    if PSQL_LOCK_FILE.exists():
        PSQL_LOCK_FILE.unlink()

    if PSQL_SOCKET_FILE.exists():
        PSQL_SOCKET_FILE.unlink()

    if REDIS_SOCKET_FILE.exists():
        REDIS_SOCKET_FILE.unlink()

    os.mknod(PSQL_SOCKET_FILE, mode=stat.S_IFSOCK)
    os.mknod(REDIS_SOCKET_FILE, mode=stat.S_IFSOCK)
    os.chown(REDIS_SOCKET_FILE,1000, 1000)
    os.chown(PSQL_SOCKET_FILE,1000, 1000)
    os.chmod(REDIS_SOCKET_FILE, 0o770)
    os.chmod(PSQL_SOCKET_FILE, 0o770)


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
            if not os.path.exists(REDIS_SOCKET_FILE) or not os.path.exists(PSQL_SOCKET_FILE):
                _create_socket_files()
            if (not os.path.exists(PROJECT_DIR / '.certs/rootCA.pem') or
                    not os.path.exists(PROJECT_DIR / '.certs/localhost.pem') or
                    not os.path.exists(PROJECT_DIR / '.certs/localhost-key.pem')):
                subprocess.run(['cd', f"{PROJECT_DIR / '.certs'}", '&&', './generate_ssl_certs_development.sh'])
        elif prod_env:
            self.stdout.write(self.style.SUCCESS('Setting up AHS production server...'))
        #call_command('dockercompose', '--setup', '--start')
        call_command('makemigrations')
        call_command('migrate')
        call_command('createsuperuser')
        call_command('populate')
