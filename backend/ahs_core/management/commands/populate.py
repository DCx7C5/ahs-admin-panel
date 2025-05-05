import getpass
import os.path
import logging
import requests

from django.urls import get_resolver
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.core.management.commands.check import Command as CheckCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand

from backend.ahs_core.models.apps import App
from backend.ahs_auth.models.authmethod import AuthMethod

from backend.ahs_endpoints.models import EndPoint
from backend.ahs_network.hosts.models import Host
from backend.ahs_network.ipaddresses.models import IPAddress

from backend.apps.bookmarks.models import BookmarksProfile
from backend.apps.workspaces.models import Workspace
from secrets import compare_digest

logger = logging.getLogger(__name__)

User = get_user_model()


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
                if not endpoint_path.endswith("/"):  # Ensure the path has a trailing slash
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
    help = ("Populate the core_appmodel table with all models in the backend apps, "
            "ensuring valid object_id values, localhost entry, and superuser creation.")

    def _ask_for_password(self):
        password = getpass.getpass(
            'Please enter password for new superuser:\n' +
            self.style.SUCCESS('>>> ')
        )
        password2 = getpass.getpass(
            'Please confirm password for new superuser:\n' + self.style.SUCCESS('>>> '))
        while not compare_digest(password, password2):
            password = getpass.getpass(
                'Passwords do not match. Please enter password for new superuser:\n' +
                self.style.SUCCESS('>>> ')
            )
            password2 = getpass.getpass(
                'Please confirm password for new superuser:\n' +
                self.style.SUCCESS('>>> ')
            )
        return password

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
            CheckCommand().run_from_argv(argv=["manage.py", "check"])
            self.populate_auth_methods_table()
            self.populate_workspace_table()
            self.populate_bookmarksprofile_table()
            self.populate_host_and_ipaddress_table()
            self.populate_apps_table()
            populate_endpoints()
            self.load_bookmark_fixtures()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

    def load_bookmark_fixtures(self):
        """
        Load bookmark fixtures from a predefined JSON file and update/create bookmarks
        in the database. If the fixture file is missing, skips the operation and
        provides a notice.
        """
        path = "backend/apps/bookmarks/fixtures/bookmarks.json"
        path_exists = os.path.exists(path)
        if path_exists:
            self.stdout.write(self.style.SUCCESS("bookmarks fixture found! Creating/Updating bookmarks now..."))
            LoadDataCommand().run_from_argv(argv=["manage.py", "loaddata", path])
        else:
            self.stdout.write(self.style.NOTICE("Bookmarks fixture not found. Skipping creation."))

    def populate_auth_methods_table(self):
        """
        Populates the AuthMethod table in the database with default authentication methods if it is empty.

        This method checks if there are existing AuthMethod entries in the database. If no entries exist,
        it creates new entries for "keybase", "email", and "webauthn" authentication methods. If entries
        already exist, the method skips the creation process.

        Raises:
            ProtectedError: If there are issues during the database query or write operations.

        """
        exists = AuthMethod.objects.exists()
        if not exists:
            self.stdout.write(self.style.WARNING("No authmethod found. Creating a new one now..."))
            AuthMethod.objects.bulk_create(objs=[AuthMethod(name="keybase"), AuthMethod(name="email"), AuthMethod(name="webauthn")])
            self.stdout.write(self.style.SUCCESS("Successfully populated auth_accounts_authmethods table."))
        else:
            self.stdout.write(self.style.SUCCESS("AuthMethod models found. Skipping creation."))

    def populate_apps_table(self):
        """
        Populates the apps table in the database with relevant records based on content types
        defined in the system. If the apps table already has existing records, no changes
        are made. Otherwise, it iterates over all content types, creating entries for
        each corresponding model.

        Checks if the apps table is already populated before attempting to create or
        update records. For each ContentType, retrieves its model class and evaluates its
        details, including the application label, model name, primary key field, and the
        first object's primary key value. These details are used to either create or update
        entries in the apps table.
        """
        exists = App.objects.exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No appmodel found. Creating a new one now..."))

            for content_type in ContentType.objects.all():
                model_class = content_type.model_class()

                if model_class is None:
                    continue

                app_label = content_type.app_label
                model_name = model_class.__name__
                primary_key_field = model_class._meta.pk.name  # noqa: protected-access

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

    def populate_bookmarksprofile_table(self):
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

    def populate_workspace_table(self):
        """
        Ensures the presence of a default workspace for the system. If no default workspace
        exists, this function creates one with predefined parameters. Otherwise, it confirms
        the existence of the workspace and skips creation.
        """
        exists = Workspace.objects.filter(owner_id__exact=1, default__exact=True).exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No default workspace found. Creating a new one now..."))
            Workspace.objects.create(owner_id=1, default=True)
        else:
            self.stdout.write(self.style.SUCCESS("Workspace found. Skipping creation."))

    def populate_host_and_ipaddress_table(self):
        """
        Populates the core_host table with localhost information if no localhost entry
        exists. It creates a new entry for localhost, assigns internal and external IP
        addresses, and ensures proper saving of the entry.
        """
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
