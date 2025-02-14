import os
import secrets
from socket import gethostbyname_ex, gethostname

from .settings import *

# load project ahs_settings from .env file
PROJECT_NAME = os.getenv('PROJECT_NAME', 'ahs-admin-panel')
ENVIRONMENT = os.getenv('AHS_ENV', 'development')

# choose between 'daphne', 'hypercorn', 'django'
HTTP_SERVER = os.getenv('AHS_SERVER', 'hypercorn')

# choose between 'trio' and 'asyncio'
HTTP_EVENT_LOOP = os.getenv('EVENT_LOOP', 'trio')
WS_EVENT_LOOP = os.getenv('WS_EVENT_LOOP', 'trio')

# ECC cryptography related settings
CRYPTO_BACKEND = os.getenv('CRYPTO_BACKEND', 'backend.ahs_crypto.engine.Cryptography')
CRYPTO_TOKEN_SIGNING_KEY = os.getenv('CRYPTO_TOKEN_SIGNING_KEY', )
CRYPTO_CURVE = os.getenv('CRYPTO_CURVE', 'secp521r1')
CRYPTO_ROOT_PRIVKEY_PATH = os.getenv('CRYPTO_ROOT_PRIVKEY_PATH', BASE_DIR / 'root.private.key')
CRYPTO_ROOT_PUBKEY_PATH = os.getenv('CRYPTO_ROOT_PUBKEY_PATH', BASE_DIR / 'root.public.key')


################################################################

if DEBUG:
    from .development import *
#elif not DEBUG and ENVIRONMENT == 'production':
#    from .production import *


if DEBUG:
    hostname, _, ips = gethostbyname_ex(gethostname())
    ipl = [ip[: ip.rfind(".")] + ".1" for ip in ips]
    INTERNAL_IPS += ipl
    ALLOWED_HOSTS += [hostname, '0.0.0.0', 'localhost'] + ipl
