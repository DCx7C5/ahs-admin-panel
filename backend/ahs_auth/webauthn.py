from django.conf import settings
from webauthn.helpers.cose import COSEAlgorithmIdentifier


PROTOCOL = 'http' if settings.DEBUG else 'https'
PORT = ':8000' if settings.DEBUG else ''

RP_NAME = settings.SITE_NAME
EXPECTED_RP_ID = settings.DOMAIN_NAME
EXPECTED_ORIGIN = [f"{PROTOCOL}://{host}{PORT}" for host in settings.ALLOWED_HOSTS]
SUPPORTED_ALGOS = [
    COSEAlgorithmIdentifier.ECDSA_SHA_512,
    COSEAlgorithmIdentifier.ECDSA_SHA_256,
    COSEAlgorithmIdentifier.EDDSA,
    COSEAlgorithmIdentifier.RSASSA_PSS_SHA_512,
]
