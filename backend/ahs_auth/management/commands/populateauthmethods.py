from django.core.management import BaseCommand

from backend.ahs_auth.models import AuthMethod


class Command(BaseCommand):
    help = "Populates the auth_method table with initial data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Populate auth_method table...")
        exists = AuthMethod.objects.exists()

        if not exists:
            AuthMethod.objects.bulk_create(objs=[AuthMethod(name="keybase"), AuthMethod(name="email"), AuthMethod(name="webauthn")])
            self.stdout.write(self.style.SUCCESS("Successfully populated auth_methods table."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))
