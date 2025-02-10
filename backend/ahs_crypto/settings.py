from cryptography.hazmat.primitives.asymmetric import ec
from django.conf import settings

from backend.ahs_crypto.apps import AhsCryptoConfig

PROJECT_DIR = settings.BASE_DIR

REQUIRED_SETTINGS = [
    'ECC_BACKEND',
]

DEFAULTS = {
    'ECC_BACKEND': None,
    'ECC_CURVE_NAME': ec.SECP256R1,
    'ECC_ROOT_PRIVKEY_PATH': PROJECT_DIR / 'private_key.pem',
    'ECC_ROOT_PUBKEY_PATH': PROJECT_DIR / 'public_key.pem',
    'ECC_DB_ENCODING': 'DER',
    'ECC_FILE_ENCODING': 'PEM',
    'ECC_PRIVKEY_MODEL': 'PrivateKey',
    'ECC_PUBKEY_MODEL': 'PublicKey',
}

ECC_BACKEND = getattr(settings, 'ECC_BACKEND')
ECC_CURVE_NAME = getattr(settings, 'ECC_CURVE_NAME', DEFAULTS['ECC_CURVE_NAME'])
ECC_ROOT_PRIVKEY_PATH = getattr(settings, 'ECC_ROOT_PRIVKEY_PATH', DEFAULTS['ECC_ROOT_PRIVKEY_PATH'])
ECC_ROOT_PUBKEY_PATH = getattr(settings, 'ECC_ROOT_PUBKEY_PATH', DEFAULTS['ECC_ROOT_PUBKEY_PATH'])
ECC_DB_ENCODING = getattr(settings, 'ECC_DB_ENCODING', DEFAULTS['ECC_DB_ENCODING'])
ECC_FILE_ENCODING = getattr(settings, 'ECC_FILE_ENCODING', DEFAULTS['ECC_FILE_ENCODING'])
ECC_PRIVKEY_MODEL = getattr(settings, 'ECC_PRIVKEY_MODEL', DEFAULTS['ECC_PRIVKEY_MODEL'])
