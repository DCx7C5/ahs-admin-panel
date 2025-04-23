from django.conf import settings

from webauthn.helpers.cose import COSEAlgorithmIdentifier


RP_NAME = settings.SITE_NAME
EXPECTED_RP_ID = settings.DOMAIN_NAME
EXPECTED_ORIGIN = [f"https://{host}" for host in settings.ALLOWED_HOSTS]
SUPPORTED_ALGOS = [
    COSEAlgorithmIdentifier.EDDSA,
    COSEAlgorithmIdentifier.ECDSA_SHA_512,
    COSEAlgorithmIdentifier.ECDSA_SHA_256,
    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_512,
]
