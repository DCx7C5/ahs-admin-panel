from django.core.management import BaseCommand
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand
from backend.ahs_core.management.commands.populateall import Command as PopulateCommand
from backend.ahs_core.management.commands.cleanmigrations import Command as CleanMigrationsCommand
from backend.ahs_core.utils import get_all_core_apps, get_all_plugin_apps, Docker


class Command(BaseCommand):
    help = "Shortcut command that executes makemigrations and migrate commands."

    def add_arguments(self, parser):

        parser.add_argument(
            '--clean',
            action='store_true',
            default=False,
            help="Delete migrations before making migrations.",
        )

        parser.add_argument(
            '--purge',
            action='store_true',
            default=False,
            help="Delete database and delete migrations before making migrations.",
        )

        parser.add_argument(
            "--populate",
            action='store_true',
            default=False,
            help="Populate database after making migrations.",
        )

    def handle(self, *args, **options):
        if options['clean']:
            CleanMigrationsCommand().run_from_argv(['manage.py', 'cleanmigrations'])
        elif options['purge']:
            CleanMigrationsCommand().run_from_argv(['manage.py', 'cleanmigrations', '--purge'])
        self.stdout.write(self.style.WARNING('Creating migrations...'))
        all_apps = get_all_core_apps() + get_all_plugin_apps()
        MakeMigrationsCommand().run_from_argv(['manage.py', 'makemigrations'] + all_apps)
        self.stdout.write(self.style.SUCCESS('Creating migrations... Done'))
        self.stdout.write(self.style.WARNING('Migrating...'))
        MigrateCommand().run_from_argv(['manage.py', 'migrate'])
        self.stdout.write(self.style.SUCCESS('Migrating... Done'))
        if options['populate']:
            PopulateCommand().run_from_argv(['manage.py', 'populate'])
