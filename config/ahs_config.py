import os
from socket import gethostbyname_ex, gethostname

from .settings import *

# load project ahs_settings from .env file
PROJECT_NAME = os.getenv('PROJECT_NAME', 'ahs_admin_panel')
ENVIRONMENT = os.getenv('AHS_ENV', 'development')

# choose between 'daphne', 'hypercorn', 'django'
HTTP_SERVER = os.getenv('AHS_SERVER', 'hypercorn')

# choose between 'trio' and 'asyncio'
HTTP_EVENT_LOOP = os.getenv('EVENT_LOOP', 'trio')
WS_EVENT_LOOP = os.getenv('WS_EVENT_LOOP', 'trio')

# docker specific ahs_settings
DOCKER_POSTGRES = os.getenv('DOCKER_DB', None)
DOCKER_REDIS = os.getenv('DOCKER_REDIS', None)
DOCKER_NODE = os.getenv('DOCKER_NODE', None)

DOCKER_SERVICE_NAME = os.getenv('SERVICE_NAME', 'ahs-admin-panel')

DOCKER_ENV = not os.getenv('NO_DOCKER', False)
NO_ASGI = os.getenv('NO_ASGI', False)

# ECC cryptography related settings
ECC_BACKEND = os.getenv('ECC_BACKEND', 'backend.ahs_crypto.ecc.ECC')
ECC_PRIVKEY_MODEL = os.getenv('ECC_PRIVKEY_MODEL', 'ahs_crypto.PrivateKey')
ECC_CURVE_NAME = os.getenv('ECC_CURVE_NAME', 'secp521r1')
ECC_ROOT_PATH = os.getenv('ECC_ROOT_PATH', BASE_DIR / 'private_key.pem')
ECC_DB_FIELD_ENCODING = os.getenv('ECC_DB_FIELD_ENCODING', 'der')


################################################################

if DEBUG:
    from .development import *
#elif not DEBUG and ENVIRONMENT == 'production':
#    from .production import *


if DOCKER_ENV and DEBUG:
    hostname, _, ips = gethostbyname_ex(gethostname())
    ipl = [ip[: ip.rfind(".")] + ".1" for ip in ips]
    INTERNAL_IPS += ipl
    ALLOWED_HOSTS += [hostname, '0.0.0.0', 'localhost'] + ipl
