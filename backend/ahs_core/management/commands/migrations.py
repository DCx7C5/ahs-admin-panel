import os
import shutil

from django.core.management import BaseCommand
from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from django.core.management.commands.migrate import Command as MigrateCommand

from backend.ahs_core.utils import get_all_core_apps, get_all_plugin_apps



class Command(BaseCommand):
    help = "Executes makemigrations and migrate commands to clean up migration directories and contents."


    def handle(self, *args, **options):

        self.stdout.write(self.style.WARNING('Creating migrations...'))

        all_apps = get_all_core_apps() + get_all_plugin_apps()
        print(all_apps)

        MakeMigrationsCommand().run_from_argv(['manage.py', 'makemigrations'] + all_apps)
        self.stdout.write(self.style.SUCCESS('Creating migrations... Done'))
        self.stdout.write(self.style.WARNING('Migrating...'))
        MigrateCommand().run_from_argv(['manage.py', 'migrate'] +all_apps)
        self.stdout.write(self.style.SUCCESS('Migrating... Done'))

