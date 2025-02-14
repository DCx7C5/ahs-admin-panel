import subprocess
from getpass import getpass

from django.core.management import BaseCommand
from django.conf import settings
from secrets import compare_digest

from backend.ahs_crypto.ecc import derive_from_private_root_key


class Command(BaseCommand):
    help = "Run ASGI server"

    def handle(self, *args, **options):
        green = self.style.SUCCESS
        password = getpass("Enter Root PrivateKey password:\n" + green('>>> '))
        password2 = getpass("Confirm password:\n" + green('>>> '))
        while not compare_digest(password, password2):
            self.stdout.write(self.style.ERROR('Passwords do not match.'))
            password = getpass("Enter Root PrivateKey password again:\n" + green('>>> '))
            password2 = getpass("Confirm password:\n" + green('>>> '))

        privroot = derive_from_private_root_key(password)
        pubroot = privroot.get_public_key()
        settings.SIMPLE_JWT['SIGNING_KEY'] = privroot
        settings.SIMPLE_JWT['VERIFYING_KEY'] = pubroot
        self.stdout.write(self.style.SUCCESS('Signingkey derived successfully.'))
        try:
            subprocess.run(['python', 'manage.py', 'runserver'])
        except KeyboardInterrupt:
            pass
        finally:
            settings.SIMPLE_JWT['SIGNING_KEY'] = None
