import os.path

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuserCommand
from django.core.management.commands.check import Command as CheckCommand
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand
from backend.apps.bookmarks.models import BookmarksProfile
from backend.core.models import (
    IPAddress, 
    Host, 
    App, 
    Workspace,
    Page,
    AHSEndPoint,
    AHSSettings,
)

AHSUser = get_user_model()

class Command(BaseCommand):
    help = "Populate the core_appmodel table with all models in the backend apps, ensuring valid object_id values, localhost entry, and superuser creation."

    def handle(self, *args, **kwargs):
        """
        Handles the initialization and setup tasks necessary for the proper functioning of the application.
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

            # Step 1: Check for superuser existence
            self.ensure_superuser()

            # Step 2: Check for default workspace of superuser
            self.ensure_workspace()

            # Step 3: Check for localhost IP Address
            self.ensure_ipaddress()

            # Step 4: Check for bookmarksprofile
            self.ensure_bookmarksprofile()

            # Step 5: Check for localhost host entry
            self.ensure_localhost()

            # Step 6: Check for Apps
            self.ensure_appmodel()

            all_apps = App.objects.values_list('label', flat=True).distinct()

            # Step 7: Check for Pages
            self.ensure_pages()

            # Step 8: Check for Endpoints
            self.ensure_endpoints()

            # Step x: import bookmarks fixtures
            self.ensure_bookmark_fixtures()

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

    def ensure_endpoints(self):
        exists = AHSEndPoint.objects.exists()
        if not exists:
            self.stdout.write(self.style.WARNING("No endpoints found. Creating a new one now..."))
            ep = AHSEndPoint.objects.create(
                path="/",
                active=True,
            )
            AHSEndPoint.objects.create(
                path="dashboard/",
                active=True,
                parent=ep
            ).save()
            AHSEndPoint.objects.create(
                path="xapi/",
                active=True,
                parent=ep
            ).save()
            AHSEndPoint.objects.create(
                path="settings/",
                active=True,
                parent=ep
            ).save()
            ep.save()

    def ensure_pages(self):
        exists = Page.objects.exists()
        if not exists:
            self.stdout.write(self.style.WARNING("No pages found. Creating a new one now..."))
            Page.objects.create(
                name="Dashboard",
                icon="bi bi-speedometer2",
                web_socket=True,
                order=1,
                is_active=True,
            ).save()
            Page.objects.create(
                name="Dashboard",
                icon="bi bi-speedometer2",
                order=1,
                web_socket=True,
                is_active=True,
            ).save()
            Page.objects.create(
                name="Settings",
                icon="bi bi-gear",
                web_socket=True,
                order=99,
                is_active=True,
            ).save()
            Page.objects.create(
                name="XAPI",
                icon="bi bi-twitter-x",
                order=90,
                web_socket=True,
                is_active=True,
            ).save()
            self.stdout.write(self.style.SUCCESS("Successfully populated core_page table."))
        

    def ensure_bookmark_fixtures(self):
        """
        Ensures that the bookmarks fixtures are processed if they exist. If the specified
        fixture file exists in the file system, the function loads its data into the database
        using Django's `loaddata` command. If the fixture file does not exist, it logs an
        informational message indicating that the fixture will be skipped.

        Attributes:
            PATH (str): The relative path to the bookmarks fixture file.

        Methods:
            ensure_bookmark_fixtures(): Checks if the bookmarks fixture file exists.
                If so, loads it into the database; otherwise, skips the process.

        Raises:
            This function does not raise exceptions.

        Notes:
            This function utilizes the Django management command `loaddata` to load fixture
            data into the database. For more information, see the Django documentation on
            fixtures.
        """
        PATH = "backend/apps/bookmarks/fixtures/bookmarks.json"
        path_exists = os.path.exists(PATH)
        if path_exists:
            self.stdout.write(self.style.SUCCESS("bookmarks fixture found! Creating/Updating bookmarks now..."))
            LoadDataCommand().run_from_argv(argv=["manage.py", "loaddata", PATH])
        else:
            self.stdout.write(self.style.NOTICE("Bookmarks fixture not found. Skipping creation."))

    def ensure_appmodel(self):
        """
        Ensures that the App model is populated with data derived from the database's content types
        and their corresponding models. This process creates entries in the App table if they
        do not already exist or updates them as necessary.

        This function iterates over all available content types, retrieves their corresponding
        model classes, and uses the primary key of the first object in the model's queryset to
        generate an App table entry. For each App table entry created or updated, appropriate
        output messages are displayed to the user using the standard output.

        The function ensures data integrity by creating the App entries only when no pre-existing
        entries are found. Otherwise, further creation is skipped, and the user is notified.

        :param self: Reference to the class instance.
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

                primary_key_field = model_class._meta.pk.name

                first_object = model_class.objects.order_by(primary_key_field).first()
                object_id = getattr(first_object, primary_key_field, None) if first_object else None

                app_instance = App.objects.create(
                    content_type=content_type,
                    name=model_name,
                    label=app_label,
                    verbose_name=content_type.name.capitalize(),
                    object_id=object_id,
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
        """
        Ensures the presence of a localhost IP address in the IPAddress table.

        This method checks if an IP address with the value '127.0.0.1' exists in the
        database. If it does not exist, it creates a new entry for the localhost IP.
        If the address already exists, a success message is logged instead. Designed
        to maintain a default localhost entry in the IPAddress table.

        Raises:
            Any runtime or database-related errors thrown by the IPAddress model
            or its associated database operations.

        Attributes:
            address (str): Represents the IP address to be checked or created. The
                value being checked is '127.0.0.1'.
        """
        exists = IPAddress.objects.filter(address__exact="127.0.0.1").exists()

        if not exists:
            self.stdout.write(self.style.WARNING("No localhost IP found. Creating a new one now..."))
            IPAddress.objects.create(address="127.0.0.1")

        else:
            self.stdout.write(self.style.SUCCESS("IPAddress found. Skipping creation."))

    def ensure_localhost(self):
        """
        Ensures the existence of a localhost configuration in the Host table.

        This function checks for the existence of a Host object with
        `is_localhost=True`. If no such instance exists, it creates a new
        localhost entry with the data required for localhost configuration.
        Otherwise, it displays a message indicating that the localhost entry is
        already present.

        Raises:
            This function does not explicitly raise errors. However, it
            relies on the database operations of the Host model, which may
            raise operational errors if called under improper conditions.

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

    def ensure_superuser(self):
        """
        Ensure that at least one superuser exists in the system. If not, create one.
        """
        superuser_exists = AHSUser.objects.filter(is_superuser=True).exists()

        if not superuser_exists:
            self.stdout.write(self.style.WARNING("No superuser found. Creating a new one now..."))
            CreateSuperuserCommand().run_from_argv(argv=["manage.py", "createsuperuser"])
        else:
            self.stdout.write(self.style.SUCCESS("Superuser found. Skipping creation."))
