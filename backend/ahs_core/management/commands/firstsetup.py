import getpass
import stat
import os.path
import subprocess
import venv

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand

DEBUG = settings.DEBUG
PROJECT_DIR = settings.BASE_DIR
SOCKET_DIR = PROJECT_DIR / 'docker' / '.sockets'
PSQL_SOCKET_FILE = SOCKET_DIR / '.s.PGSQL.5432'
PSQL_LOCK_FILE = SOCKET_DIR / '.s.PGSQL.5432.lock'
REDIS_SOCKET_FILE = SOCKET_DIR / 'redis.sock'
VENV_DIR = PROJECT_DIR / '.venv'
CERTS_DIR = PROJECT_DIR / '.certs'
ROOTCA_FILE = CERTS_DIR / 'rootCA.pem'
LOCALHOST_KEY_FILE = CERTS_DIR / 'localhost-key.pem'
LOCALHOST_CERT_FILE = CERTS_DIR / 'localhost.pem'
PYTHON_BIN_PATH = VENV_DIR / 'bin' / 'python'


class Command(BaseCommand):
    help = 'First setup AHS, installs '

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
            if not self.check_venv_directory():
                self.create_venv_directory()
            if not self.check_socket_files():
                self.create_socket_files()
            if not self.check_ssl_certificates():
                self.create_ssl_certificates()

        elif prod_env:
            self.stdout.write(self.style.SUCCESS('Setting up AHS production server...'))

        #call_command('dockercompose', '--setup', '--start')
        call_command('makemigrations')
        call_command('migrate')
        call_command('createsuperuser')
        call_command('populate')

    def check_socket_files(self):
        if not os.path.exists(SOCKET_DIR):
            return False
        if not os.path.exists(PSQL_SOCKET_FILE):
            return False
        if not os.path.exists(REDIS_SOCKET_FILE):
            return False
        return True

    def create_socket_files(self):
        if not os.path.exists(SOCKET_DIR):
            SOCKET_DIR.mkdir(0o770)
        os.chmod(SOCKET_DIR, 0o775)

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

    def check_venv_directory(self):
        venv_dir = PROJECT_DIR / '.venv'
        if not venv_dir.exists():
            return False
        return True

    def create_venv_directory(self):
        venv.create(VENV_DIR, with_pip=True)

    def check_ssl_certificates(self):
        if (not os.path.exists(ROOTCA_FILE) or
                not os.path.exists(LOCALHOST_KEY_FILE) or
                not os.path.exists(LOCALHOST_CERT_FILE)):
            return False
        return True

    def create_ssl_certificates(self):
        subprocess.run(['cd', f"{PROJECT_DIR / '.certs'}", '&&', './generate_ssl_certs_development.sh'])

    def check_capabilities(self):
        output = subprocess.run(['getcap', PYTHON_BIN_PATH], capture_output=True, text=True)
        if 'cap_net_bind_service=+ep' in output.stdout:
            return True
        return False

    def set_capabilities(self):
        abs_path_py = os.path.abspath(PYTHON_BIN_PATH)
        if os.path.islink(PYTHON_BIN_PATH):
            self.stdout.write(f"File is a symlink. Copying link target to {PYTHON_BIN_PATH} and removing the link."
                              f"This way we can set the capabilities on the copied file only.")
            link_target = os.readlink(abs_path_py)
            os.unlink(abs_path_py)
            with open(link_target, 'rb') as f:
                data = f.read()
            with open(PYTHON_BIN_PATH, 'wb') as f:
                f.write(data)
        self.stdout.write(f"Setting capabilities on {PYTHON_BIN_PATH}")

        password = getpass.getpass("Enter your sudo password: ")
        args = ['sudo', '-S','setcap', 'cap_net_bind_service=+ep', abs_path_py]

        try:
            proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Send password with a newline
            stdout, stderr = proc.communicate(password + '\n')

            # Output handling
            if proc.returncode == 0:
                self.stdout.write(self.style.SUCCESS('Command succeeded:'))
                self.stdout.write(stdout)
            else:
                self.stdout.write(self.style.ERROR('Command failed:'))
                self.stdout.write(stderr)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
