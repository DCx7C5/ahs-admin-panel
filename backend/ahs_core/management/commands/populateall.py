import getpass
import os.path
import logging

from django.core.management import call_command
from django.urls import get_resolver
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management.commands.check import Command as CheckCommand
from django.core.management.commands.loaddata import Command as LoadDataCommand


from backend.ahs_endpoints.models import EndPoint
from backend.apps.bookmarks.models import BookmarksProfile
from secrets import compare_digest

logger = logging.getLogger(__name__)

User = get_user_model()


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

        try:
            # Step 0: Systemcheck
            CheckCommand().run_from_argv(argv=["manage.py", "check"])
            call_command("populateauthmethods")
            call_command("populateworkspaces")
            call_command("populateapps")
            #self.populate_endpoints()
            call_command("populatenetwork")
            self.populate_bookmarksprofile_table()
            self.load_bookmark_fixtures()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

    def load_bookmark_fixtures(self):
        """
        Load bookmark fixtures from a predefined JSON file and update/create bookmarks
        in the database. If the fixture file is missing, skips the operation and
        provides a notice.
        """
        self.stdout.write("Loading bookmarks fixture from JSON file...")
        path = "backend/apps/bookmarks/fixtures/bookmarks.json"
        path_exists = os.path.exists(path)
        exists = BookmarksProfile.objects.exists()
        if path_exists and not exists:
            LoadDataCommand().run_from_argv(argv=["manage.py", "loaddata", path])
            self.stdout.write(self.style.SUCCESS("Bookmarks fixture loaded successfully."))
        else:
            self.stdout.write(self.style.WARNING("Bookmarks fixture not found. Skipping creation."))

    def populate_endpoints(self):
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
        self.stdout.write("Populating endpoints table...")
        exists = EndPoint.objects.exists()

        if not exists:
            extract_paths(resolver.url_patterns)
            self.stdout.write(self.style.SUCCESS("Endpoints table populated successfully."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))

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
        self.stdout.write("Populating bookmarks table...")
        exists = BookmarksProfile.objects.filter(user_id__exact=1).exists()

        if not exists:
            BookmarksProfile.objects.create(user_id=1)
            self.stdout.write(self.style.SUCCESS("Bookmarks table populated successfully."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))
