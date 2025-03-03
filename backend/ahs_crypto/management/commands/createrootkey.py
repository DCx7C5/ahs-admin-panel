import os
import logging
from getpass import getpass
from secrets import compare_digest

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
    BestAvailableEncryption,
)
from cryptography.hazmat.primitives.asymmetric import ec

from django.core.management import BaseCommand, CommandError
from django.conf import settings as django_settings


logger = logging.getLogger(__name__)


class PrivateKeyExistsError(Exception):
    """
    Exception raised when a private key already exists.
    """
    def __init__(self, message, error=None):
        super().__init__(message)
        self.errors = error
        logger.debug(message, exc_info=error)


class Command(BaseCommand):
    help = "Create private root key based on eliptical curve SECP521R1"
    stealth_options = ("stdin",)
    engine = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false',
            default=True,
            dest='interactive',
        )

        parser.add_argument(
            "--overwrite", "--regenerate", "--force",
            action='store_true',
            dest='regenerate',
            default=False,
            help="Regenerate private key.",
        )

        parser.add_argument(
            "--out",
            action='store',
            default=django_settings.BASE_DIR,
            help="Choose output for private key (Can be filename or directory).",
        )

        parser.add_argument(
            "--password",
            action='store',
            default=None,
            help="Choose password for private key.",
        )

    def handle(self, *args, **options):

        regenerate = options['regenerate']
        out = str(options['out'])
        password = options['password']
        save_to_fs = True

        # Check for file output
        if os.path.isfile(out):
            priv_out_filename = out
        else:
            priv_out_filename = out + '/root.private.key'

        if not regenerate and os.path.exists(priv_out_filename):
            self.stdout.write(self.style.ERROR('Private key already exists. Delete old key or use --regenerate param'))
            raise CommandError('Private key already exists.')

        # Check if --output param was set
        if out != django_settings.BASE_DIR:
            save = input('Save to project directory?\n'
                         'Answering no prints keys to terminal screen [Y/n]:\n' +
                         self.style.SUCCESS(f'>>> '))
            save_to_fs = save.lower() in ('y', 'yes', '')
            if save_to_fs:
                if options['password'] is None:
                    password = getpass('Choose password for private key:\n' + self.style.SUCCESS('>>> '))
                    password2 = getpass('Confirm password:\n' + self.style.SUCCESS('>>> '))

                    while not compare_digest(password.encode(), password2.encode()):
                        password = getpass('Passwords do not match. Try again:\n' + self.style.SUCCESS('>>> '))
                        password2 = getpass('Confirm password:\n' + self.style.SUCCESS('>>> '))

        self.stdout.write('CREATING PRIVATE ROOT KEY...')
        private_key = ec.generate_private_key(ec.SECP521R1())
        if isinstance(password, str):
            password = password.encode()
        private_key_binary = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=BestAvailableEncryption(password) if password else NoEncryption()
        )

        if save_to_fs:
            self.stdout.write('SAVING PRIVATE ROOT KEY TO FILE...')
            with open(priv_out_filename, 'wb') as f:
                f.write(private_key_binary)
        else:
            self.stdout.write(private_key_binary.decode())

        self.stdout.write(self.style.SUCCESS('PRIVATE ROOT KEY CREATED.'))
