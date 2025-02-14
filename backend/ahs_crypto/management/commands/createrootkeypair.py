import os
import logging
from getpass import getpass
from secrets import compare_digest

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption,
    BestAvailableEncryption,
)
from cryptography.hazmat.primitives.asymmetric import ec

from django.core.management import BaseCommand, CommandError
from django.conf import settings as django_settings

from ...utils import get_crypto_backend


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
    help = "Create private & public root key based on eliptical curve SECP521R1"
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
            "--encoding",
            action='store',
            default=None,
            help="Choose encoding for ROOT keypair.",
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
        self.engine = get_crypto_backend()

        regenerate = options['regenerate']
        out = str(options['out'])
        encoding = options['encoding']
        password = options['password']
        priv_key_enc = pub_key_enc = "pem"
        save_to_fs = True

        # Check for file output
        if os.path.isfile(out):
            priv_out_filename = out
            if "private" in priv_out_filename:
                pub_out_filename = priv_out_filename.replace('private', 'public')
            else:
                pub_out_filename = priv_out_filename + '.pub'
        else:
            priv_out_filename = out + '/root.private.key'
            pub_out_filename = out + '/root.public.key'

        if not regenerate and os.path.exists(priv_out_filename):
            self.stdout.write(self.style.ERROR('Private key already exists. Delete old key or use --regenerate param'))
            raise CommandError('Private key already exists.')

        # Check if --output param was set
        if out != django_settings.BASE_DIR:
            save = input('Save to project directory?\n'
                         'Answering no prints keys to terminal screen [Y/n]:\n' +
                         self.style.SUCCESS(f'>>> '))
            save_to_fs = save.lower() in ('y', 'yes', '')
            if save_to_fs and not encoding:
                priv_encoding = input('Encoding for PRIVATE ROOT key file?\n'
                                 'Choices:\n'
                                 '\t 1 - PEM (default)\n'
                                 '\t 2 - DER\n' +
                                 self.style.SUCCESS('>>> '))
                pub_encoding = input('Encoding for PUBLIC ROOT key file?\n'
                                 'Choices:\n'
                                 '\t 1 - PEM (default)\n'
                                 '\t 2 - DER\n'
                                 '\t 3 - X962\n' +
                                 self.style.SUCCESS('>>> '))
                if options['password'] is None:
                    password = getpass('Choose password for private key:\n' + self.style.SUCCESS('>>> '))
                    password2 = getpass('Confirm password:\n' + self.style.SUCCESS('>>> '))

                    while not compare_digest(password.encode(), password2.encode()):
                        password = getpass('Passwords do not match. Try again:\n' + self.style.SUCCESS('>>> '))
                        password2 = getpass('Confirm password:\n' + self.style.SUCCESS('>>> '))
                if encoding is None:
                    if priv_encoding == '' or (priv_encoding.lower() in ("1", "pem")):
                        priv_key_enc = Encoding.PEM
                    elif priv_encoding.lower() == ("2" or "der"):
                        priv_key_enc = Encoding.DER
                    else:
                        raise CommandError('Invalid encoding.')

                    if pub_encoding == '' or (pub_encoding.lower() in ("1", "pem")):
                        pub_key_enc = Encoding.PEM
                    elif pub_encoding.lower() in ("2", "der"):
                        pub_key_enc = Encoding.DER
                    elif pub_encoding.lower() in ("3", "x962"):
                        pub_key_enc = Encoding.X962
                    else:
                        raise CommandError('Invalid encoding.')
                else:
                    priv_key_enc = pub_key_enc = Encoding.PEM
            else:
                priv_key_enc = Encoding.PEM
                pub_key_enc = Encoding.PEM
        self.stdout.write('CREATING PRIVATE ROOT KEY...')
        private_key = ec.generate_private_key(self.engine.curve_instance)
        if isinstance(password, str):
            password = password.encode()
        private_key_binary = private_key.private_bytes(
            encoding=priv_key_enc,
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

        self.stdout.write('CREATING PUBLIC ROOT KEY...')

        pub_format = PublicFormat.SubjectPublicKeyInfo \
            if pub_key_enc in [Encoding.PEM, Encoding.DER] \
            else PublicFormat.CompressedPoint

        public_key = private_key.public_key()
        public_key_binary = public_key.public_bytes(
            encoding=pub_key_enc,
            format=pub_format
        )
        if save_to_fs:
            self.stdout.write('SAVING PRIVATE ROOT KEY TO FILE...')
            with open(pub_out_filename, 'wb') as f:
                f.write(public_key_binary)
        else:
            self.stdout.write(public_key_binary.decode())

        self.stdout.write(self.style.SUCCESS('PUBLIC ROOT KEY CREATED'))
