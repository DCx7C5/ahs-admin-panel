from django.conf import settings


RP_NAME = settings.SITE_NAME
EXPECTED_RP_ID = 'localhost' if settings.DEBUG else settings.DOMAIN_NAMES[0]
EXPECTED_ORIGIN = settings.DOMAIN_NAMES
SUPPORTED_ALGOS = ["-7", "-257"]
