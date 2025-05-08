import logging
from logging import INFO

import requests
from requests import __version__ as requests_version
from django.core.management import BaseCommand
from django.utils import timezone

from backend.ahs_network.hosts.models import Host
from backend.ahs_network.http.models import UserAgent


logging.getLogger('urllib3.connectionpool').setLevel(INFO)


USER_AGENTS = [
    ("Chrome (Windows)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    ("Firefox (Windows)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"),
    ("Edge (Windows)", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.2478.67"),
    ("Safari (macOS)", "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"),
    ("Chrome (Linux)", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"),
    ("Firefox (Linux)", "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0"),
    ("Chrome (macOS)", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"),
    ("Chrome (Android)", "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"),
    ("Safari (iOS)", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"),
    ("Chrome (Samsung Android)", "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36"),
    ("Safari (iPadOS)", "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"),
    ("Googlebot", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"),
    ("Bingbot", "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)"),
    ("YandexBot", "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
    ("Twitterbot", "Twitterbot/1.0"),
    ("curl", "curl/7.88.1"),
    ("Wget", "Wget/1.21.1 (linux-gnu)"),
    ("python-requests", f"python-requests/{requests_version}"),
    ("Postman", "PostmanRuntime/7.36.1"),
    ("Internet Explorer 10", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)"),
    ("Nintendo Switch Browser", "Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.10.15 NintendoBrowser/5.1.0.13343"),
    ("PlayStation 4 Browser", "Mozilla/5.0 (PlayStation 4 3.11) AppleWebKit/537.73 (KHTML, like Gecko)"),
]


class Command(BaseCommand):
    help = "Populates the network database table with initial data."

    def handle(self, *args, **options):
        self.populate_useragents()
        self.populate_host_and_ipaddress_table()

    def populate_useragents(self):
        self.stdout.write("Populating user agents...")
        exists = UserAgent.objects.exists()
        if not exists:
            try:
                for name, user_agent in USER_AGENTS:
                    UserAgent.objects.bulk_create(
                        objs=[UserAgent(type=name, value=user_agent) for _ in USER_AGENTS],
                        batch_size=len(USER_AGENTS),
                    )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
            self.stdout.write(self.style.SUCCESS("User agents populated successfully."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))

    def populate_host_and_ipaddress_table(self):
        """
        Populates the core_host table with localhost information if no localhost entry
        exists. It creates a new entry for localhost, assigns internal and external IP
        addresses, and ensures proper saving of the entry.
        """
        self.stdout.write("Populating hosts and ipaddress table...")
        exists = Host.objects.filter(is_localhost=True).exists()
        now = timezone.now()
        external_ip = requests.get('https://icanhazip.com').text[:-1]

        if not exists:
            host = Host.objects.create(
                hostname="localhost",
                is_localhost=True,
                is_systemhost=False,
                created_at=now,
                updated_at=now,
            )
            extentry = host.ip_addresses.filter(address=external_ip)
            locentry = host.ip_addresses.filter(address="127.0.0.1")
            if not locentry.exists():
                host.ip_addresses.create(address="127.0.0.1")
            if not extentry.exists():
                host.ip_addresses.create(address=external_ip)
            host.save()
            self.stdout.write(self.style.SUCCESS("hosts & IP address table populated successfully."))
        else:
            self.stdout.write(self.style.WARNING("Table entry already exists. Skipping creation."))
