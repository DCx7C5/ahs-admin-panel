import getpass
import os.path
import logging
import requests
from django.contrib.auth.models import UserManager
from django.urls import get_resolver
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuserCommand
from django.core.management.commands.check import Command as CheckCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand

from backend.ahs_accounts.models import AHSUserManager
from backend.ahs_core.models.apps import App
from backend.ahs_crypto import ecc, get_private_key_model
from backend.ahs_crypto.ecc import load_private_key_from_file, derive_subkey, generate_public_key, \
    serialize_public_key_to_der, serialize_private_key_to_der
from backend.ahs_crypto.settings import ECC_ROOT_PRIVKEY_PATH
from backend.ahs_endpoints.models import EndPoint
from backend.apps.network.models.hosts import Host

from backend.apps.bookmarks.models import BookmarksProfile
from backend.apps.network.models.ipaddresses import IPAddress
from backend.apps.workspaces.models import Workspace

logger = logging.getLogger(__name__)

AHSUser = get_user_model()


def populate_endpoints():
    """
    Automatically populates the `ahs_core EndPoint` table with all ahs_endpoints from the URL resolver.
    Any duplicate entries will be skipped.
    """
    resolver = get_resolver()  # Get the URL resolver (all registered URLs)

    def extract_paths(urlpatterns, parent=None):
        """
        Recursively extract all paths from the urlpatterns.
        :param urlpatterns: List of URL patterns.
        :param parent: Parent `EndPoint` instance for hierarchical nesting (None for root).
        """
        for pattern in urlpatterns:
            if hasattr(pattern, "url_patterns"):  # Handles included URL patterns
                # Create a top-level endpoint for the included namespace
                if hasattr(pattern, 'namespace') and pattern.namespace:
                    parent_endpoint, _ = EndPoint.objects.get_or_create(
                        path=f"{pattern.namespace}/",  # Assign the namespace as the path
                        parent=parent,
                        defaults={"active": True, "order": 0}
                    )
                else:
                    parent_endpoint = parent

                # Recursively process included patterns
                extract_paths(pattern.url_patterns, parent=parent_endpoint)
            elif hasattr(pattern, "pattern"):
                # Handle individual patterns (leaf nodes)
                endpoint_path = str(pattern.pattern)
                if not endpoint_path.endswith("/"):  # Ensure path has a trailing slash
                    endpoint_path += "/"

                # Create the endpoint if it doesn't already exist
                EndPoint.objects.get_or_create(
                    path=endpoint_path,
                    parent=parent,
                    defaults={"active": True, "order": 0}
                )

    # Start extracting ahs_endpoints from the root URL resolver
    extract_paths(resolver.url_patterns)






class Command(BaseCommand):
    help = "Populate the core_appmodel table with all models in the backend apps, ensuring valid object_id values, localhost entry, and superuser creation."


    def handle(self, *args, **kwargs):
        """
        Handles the initialization and setup ahs_tasks necessary for the proper functioning of the application.
        Checks for required configurations, default entities, and performs data consistency operations.

        Summary:
        The handle function performs the following operations sequentially:
        1. Runs a system check to ensure the application environment is configured correctly.
        2. Verifies the presence of a superuser in the system.
        3. Checks for the default workspace associated with the superuser.
        4. Ensures the existence of a localhost IP address in the system configuration.
        5. Validates the bookmarks profile used within the application.
        6. Verifies the presence of a localhost host entry.
        7. Ensures that application models are properly configured.
        8. Imports default bookmarks fixtures.

        Parameters:
        *args : tuple
            Variable length argument list, unused in this implementation.
        **kwargs : dict
            Arbitrary keyword arguments, unused in this implementation.

        Raises:
        Exception
            Any exception that occurs during the execution of the steps is caught and logged.
        """
        try:
            # Step 0: Systemcheck
            CheckCommand().run_from_argv(
                argv=["manage.py", "check"])

            self.ensure_superuser()
            self.ensure_workspace()
            self.ensure_ipaddress()
            self.ensure_bookmarksprofile()
            self.ensure_localhost()
            self.ensure_appmodel()
            populate_endpoints()
            self.ensure_bookmark_fixtures()

            self.ensure_system_keypair()

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

    def ensure_superuser(self):
        """
        Ensure that at least one superuser exists in the system. If not, create one.
        """
        superuser_exists = AHSUser.objects.filter(is_superuser=True).exists()

        if not superuser_exists:
            self.stdout.write(self.style.WARNING("No superuser found. Creating a new one now..."))
            username = getpass.getpass('Please enter username for new superuser: ')
            email = getpass.getpass('Please enter email for new superuser: ')
            password = getpass.getpass('Please enter password for new superuser: ')
            try:
                AHSUserManager().create_superuser(username=username, email=email, password=password)
            except Exception as e:
                raise CommandError('Superuser creation FAILED') from e
            else:
                self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser found. Skipping creation."))


    def ensure_bookmark_fixtures(self):

        PATH = "backend/apps/bookmarks/fixtures/bookmarks.json"
        path_exists = os.path.exists(PATH)
        if path_exists:
            self.stdout.write(self.style.SUCCESS("bookmarks fixture found! Creating/Updating bookmarks now..."))
            LoadDataCommand().run_from_argv(argv=["manage.py", "loaddata", PATH])
        else:
            self.stdout.write(self.style.NOTICE("Bookmarks fixture not found. Skipping creation."))

    def ensure_appmodel(self):
        exists = App.objects.exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No appmodel found. Creating a new one now..."))

            for content_type in ContentType.objects.all():
                model_class = content_type.model_class()

                if model_class is None:
                    continue

                app_label = content_type.app_label
                model_name = model_class.__name__
                primary_key_field = model_class._meta.pk.name

                first_object = model_class.objects.order_by(primary_key_field).first()

                # Ensure object_id always has a value
                object_id = getattr(first_object, primary_key_field, None) if first_object else 0  # Default to 0

                app_instance = App.objects.create(
                    content_type=content_type,
                    name=model_name,
                    label=app_label,
                    verbose_name=content_type.name.capitalize(),
                )

                if app_instance:
                    self.stdout.write(self.style.SUCCESS(
                        f"Added: {app_label}.{model_name} (object_id: {object_id})"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Updated: {app_label}.{model_name} (object_id: {object_id})"
                    ))

            self.stdout.write(self.style.SUCCESS("Successfully populated core_appmodel table."))
        else:
            self.stdout.write(self.style.SUCCESS("Appmodel found. Skipping creation."))

    def ensure_bookmarksprofile(self):
        """
        Ensures that a `BookmarksProfile` object exists for the superuser.

        This function checks if a `BookmarksProfile` is present for a user
        with `user_id` equal to 1. If it does not exist, a new `BookmarksProfile`
        is created, and a warning message is logged. If the profile is already
        present, a success message is logged, and no action is taken.

        Raises:
            None: Does not raise any exceptions explicitly.
        """
        exists = BookmarksProfile.objects.filter(user_id__exact=1).exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No bookmarksprofile found for superuser . Creating a new one now..."))
            BookmarksProfile.objects.create(user_id=1)
        else:
            self.stdout.write(self.style.SUCCESS("Superuser found. Skipping creation."))

    def ensure_workspace(self):
        """
        Ensures the presence of a default workspace for the system. If no default workspace
        exists, this function creates one with predefined parameters. Otherwise, it confirms
        the existence of the workspace and skips creation.

        Methods
        -------
        ensure_workspace()
            Checks for the existence of a default workspace belonging to the owner with ID 1.
            Creates a new default workspace if none exists, or confirms the presence of an
            existing workspace.

        Raises
        ------
        Exception
            If database operations fail during the creation or verification steps, an exception
            is raised depending on the supporting database backend or its integrity constraints.
        """
        exists = Workspace.objects.filter(owner_id__exact=1, default__exact=True).exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No default workspace found. Creating a new one now..."))
            Workspace.objects.create(owner_id=1, default=True)
        else:
            self.stdout.write(self.style.SUCCESS("Workspace found. Skipping creation."))

    def ensure_ipaddress(self):
        exists = IPAddress.objects.filter(address__exact="127.0.0.1").exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No localhost IP found. Creating a new one now..."))
            IPAddress.objects.create(address="127.0.0.1")

        else:
            self.stdout.write(self.style.SUCCESS("IPAddress found. Skipping creation."))

    def ensure_localhost(self):

        exists = Host.objects.filter(is_localhost=True).exists()
        now = timezone.now()
        external_ip = requests.get('https://icanhazip.com').text[:-1]

        if not exists:
            self.stdout.write(self.style.WARNING("No localhost found. Creating a new one now..."))
            host = Host.objects.create(
                hostname="localhost",
                is_localhost=True,
                is_systemhost=False,
                created_at=now,
                updated_at=now,
            )
            extentry = host.ip_addresses.filter(address=external_ip)
            locentry = host.ip_addresses.filter(address="127.0.0.1")
            if not extentry.exists():
                host.ip_addresses.create(address=external_ip)
            if not locentry.exists():
                host.ip_addresses.create(address="127.0.0.1")
            host.save()

            self.stdout.write(self.style.SUCCESS("Successfully populated core_host table."))

        else:
            self.stdout.write(self.style.SUCCESS("Localhost found. Skipping creation."))


    def ensure_system_keypair(self, password):
        PrivateKey = get_private_key_model()  # noqa

        root_key = load_private_key_from_file(ECC_ROOT_PRIVKEY_PATH, password)
        exists = PrivateKey.objects.exists()
        if not exists:
            self.stdout.write(self.style.WARNING("No system keypair found. Deriving new private key from root key..."))
            sys_priv = derive_subkey(root_key, 0)
            self.stdout.write(self.style.SUCCESS("Successfully derived private key from root key."))
            self.stdout.write(self.style.SUCCESS("Generating public key from derived private key..."))
            sys_pub = generate_public_key(sys_priv)
            self.stdout.write(self.style.SUCCESS("Successfully generated public key from derived private key."))
            self.stdout.write(self.style.SUCCESS("Serializing keys to DER format..."))
            ser_sys_pub = serialize_public_key_to_der(sys_pub)
            ser_sys_priv = serialize_private_key_to_der(sys_priv, password)
            self.stdout.write(self.style.SUCCESS("Successfully serialized keys to DER format."))
            self.stdout.write(self.style.SUCCESS("Creating private key model object..."))
            PrivateKey.objects.create(
                private_key=ser_sys_priv,
                public_key=ser_sys_pub,
            )
            self.stdout.write(self.style.SUCCESS("Successfully created private key model object."))



