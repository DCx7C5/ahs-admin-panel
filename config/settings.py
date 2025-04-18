import os
import secrets
from _socket import gethostbyname_ex, gethostname
from datetime import timedelta
from os import environ
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management import ManagementUtility
from dotenv import load_dotenv

from backend.ahs_core.ecc import load_private_key_from_file, derive_from_private_root_key, derive_subkey

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('SECRET_KEY')

RUNTIME_SECRET_KEY = secrets.token_urlsafe(48)



INSTALLED_APPS = [
    # ASGI Server
    'daphne',
    'backend.ahs_core',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',

    # django channels
    'channels',
    'channels_redis',

    # django rest api
    'rest_framework',
    'adrf',
    'corsheaders',

    # webpack
    'webpack_loader',

    # Toolbar Plugins/Modules
    'debug_toolbar',
    'graphene_django',

    # Core Apps

    'backend.ahs_api',
    'backend.ahs_network',
    'backend.ahs_network.domains',
    'backend.ahs_network.hosts',
    'backend.ahs_network.ipaddresses',
    'backend.ahs_channels',
    'backend.ahs_endpoints',
    'backend.ahs_settings',
    'backend.ahs_socket_conns',
    'backend.ahs_tasks',
    'backend.ahs_workers',

    # Apps / Plugins
    'backend.apps',
    'backend.apps.bookmarks',
    'backend.apps.osint',
    'backend.apps.system',
    'backend.apps.system.cpu',
    'backend.apps.system.filesystem',
    'backend.apps.system.docker',
    'backend.apps.system.security',
    'backend.apps.workspaces',
    'backend.apps.xapi',
]
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(environ.get('DEBUG'))

SITE_NAME = 'AHSAdminPanel'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST', None),
        'PORT': os.environ.get('DB_PORT', None),
    }
}

MIDDLEWARE = [
    'backend.ahs_core.middleware.AsyncRequestLoggerMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'backend.ahs_core.middleware.SessionAuthMsgsMiddleware',
    'backend.ahs_core.middleware.AHSMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# We don't use built-in SessionMiddleware, AuthenticationMiddleware and MessagesMiddleware,
# which throw error on startup when missing in MIDDLEWARE list.
SILENCED_SYSTEM_CHECKS = [
    'admin.E410',
    'admin.E408',
    'admin.E409',
]

ROOT_URLCONF = 'adminpanel.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'backend.ahs_core.context_processors.debug',
            ],
        },
    },
]

ASGI_APPLICATION = 'adminpanel.asgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'webpack_bundles/',  # must end with slash
        'STATS_FILE': os.path.join(BASE_DIR, 'frontend/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
        'LOADER_CLASS': 'webpack_loader.loader.WebpackLoader',
    }
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_HOST')],
            # "password": os.environ.get('REDIS_PASS'),
        },
        "prefix": "ahs_channel",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_HOST'),
        "TIMEOUT": 3600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'accounts/login'
LOGIN_URL = 'accounts/login'
LOGOUT_URL = 'accounts/logout'

AUTH_USER_MODEL = "ahs_core.AHSUser"

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_ENGINE_AHS = 'backend.ahs_core.engines'
SESSION_MODEL_AHS = "ahs_core.AHSSession"
SESSION_TOKEN_EXPIRATION_TIME = 60 * 60 * 24 * 7  # 7 days
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

SESSION_COOKIE_PATH = '/admin'
SESSION_COOKIE_PATH_AHS = '/'
SESSION_COOKIE_NAME_AHS = 'ahssessionid'


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {name} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'rotating_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'adminpanel.log',
            'maxBytes': 1024 * 1024 * 100,
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console', 'rotating_file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'rotating_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'asyncio': {
            'level': 'INFO',  # INFO to suppress early initialisation logs. Set to DEBUG again in cmd_parser.py.
        },
        'backend.ahs_core': {
            'level': 'DEBUG',
            'propagate': True,
        },
        'backend.ahs_core.consumers.cmd_parser': {
            'level': 'INFO',  # INFO to suppress early initialisation logs. Set to DEBUG again in cmd_parser.py.
            'handlers': ['console', 'rotating_file'],
            'propagate': False,  # Prevent logs from duplicating in `backend.ahs_core`
        },
    },
}

# security related stuff
ROOT_PRIVKEY_PATH = environ.get('ROOT_PRIVKEY_PATH', 'root.private.key')
if not os.path.exists(ROOT_PRIVKEY_PATH):
    raise ImproperlyConfigured(f"Root private key file '{ROOT_PRIVKEY_PATH}' does not exist.")

SESSION_COOKIE_SECURE = False if DEBUG else True
SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_SECURE = False if DEBUG else True
CSRF_COOKIE_HTTPONLY = False if DEBUG else True
SECURE_CONTENT_TYPE_NOSNIFF = False if DEBUG else True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True if DEBUG else False
CORS_ALLOWED_ORIGINS = ["http://localhost:8000", "http://localhost:3000",]
CORS_ORIGIN_WHITELIST = ['http://localhost:8000', 'http://localhost:3000',]
GRAPHENE = {'SCHEMA': 'ahs_core.schema.schema'}
INTERNAL_IPS = ['127.0.0.1',]
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

PROJECT_NAME = os.getenv('PROJECT_NAME', 'ahs-admin-panel')
ENVIRONMENT = os.getenv('AHS_ENV', 'development' if DEBUG else 'production')
CRYPTO_BACKEND = 'ECC'


# choose between 'daphne', 'hypercorn', 'django'
HTTP_SERVER = os.getenv('AHS_SERVER', 'hypercorn')

# choose between 'trio' and 'asyncio'
HTTP_EVENT_LOOP = os.getenv('EVENT_LOOP', 'trio')
WS_EVENT_LOOP = os.getenv('WS_EVENT_LOOP', 'trio')


if DEBUG:
    hostname, _, ips = gethostbyname_ex(gethostname())
    ipl = [ip[: ip.rfind(".")] + ".1" for ip in ips]
    INTERNAL_IPS += ipl
    ALLOWED_HOSTS += [hostname, '0.0.0.0', 'localhost'] + ipl
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += (
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
