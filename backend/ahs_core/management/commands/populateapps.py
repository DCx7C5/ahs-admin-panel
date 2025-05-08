from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from backend.ahs_core.models import App


class Command(BaseCommand):
    help = "Populates the apps database table with initial data."

    def handle(self, *args, **options):
        self.stdout.write("Populating apps table...")
        exists = App.objects.exists()

        if not exists:
            try:
                for content_type in ContentType.objects.all():
                    model_class = content_type.model_class()

                    if model_class is None:
                        continue

                    app_label = content_type.app_label
                    model_name = model_class.__name__

                    App.objects.create(
                        content_type=content_type,
                        name=model_name,
                        label=app_label,
                        verbose_name=content_type.name.capitalize(),
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
            self.stdout.write(self.style.SUCCESS("Apps populated successfully."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))
