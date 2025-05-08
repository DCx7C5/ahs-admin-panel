from django.core.management import BaseCommand

from backend.ahs_core.models.workspaces import Workspace


class Command(BaseCommand):
    help = "Populates the network database table with initial data."

    def handle(self, *args, **options):
        self.stdout.write("Populating workspaces table...")
        exists = Workspace.objects.filter(owner_id__exact=1, default__exact=True).exists()
        if not exists:
            try:
                Workspace.objects.create(owner_id=1, default=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
            self.stdout.write(self.style.SUCCESS("Workspacess populated successfully."))
            return
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))
