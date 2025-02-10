import os
import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from django.core.management import BaseCommand, CommandError
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperUserCommand
from config.settings import BASE_DIR


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
    help = "Create private key based on eliptical curve SECP521R1"
    stealth_options = ("stdin",)

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
            "--encoding",
            action='store',
            default='pem',
            choices=['der', 'pem', 'DER', 'PEM', 'OpenSSH'],
            help="Choose encoding for private key.",
        )
        parser.add_argument(
            "--ouput",
            action='store',
            default=f'private_key.pem',
            help="Choose format for private key.",
        )
        parser.add_argument(
            "--password",
            action='store',
            default=None,
            help="Choose password for private key.",
        )

    def handle(self, *args, **options):
        regenerate = options['regenerate']
        output_filename = f'{options["ouput"]}.{options["encoding"].lower()}'

        if not regenerate and os.path.exists(output_filename):

            self.stdout.write('Private key already exists. Delete old key or use', self.style.ERROR)
            raise CommandError('Private key already exists.')
        self.stdout.write(self.style.NOTICE('CREATING PRIVATE KEY...'))
        private_key = ec.generate_private_key(ec.SECP521R1())
        private_key_binary = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(options['password'].encode()) \
                if options['password'] else serialization.NoEncryption()
        )
