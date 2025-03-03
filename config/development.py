import os
from pathlib import Path
from socket import gethostbyname_ex, gethostname

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'
DEBUG = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8000',
    'http://localhost:3000',  # The default port for create-react-app
]
# Database

# DB_HOST and DB_PORT env vars must be None in order to connect over system socket,
# which is faster (missing network stack).
#
# The DB container forwards host port 5433 to container port 5432 to be able to connect
# with a database manager without conflicting the port of a potential host postgresql database.
# django.db.backends.postgresql supports psycopg3 natively.

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

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enable Browsable API
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '0.1.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

GRAPHENE = {
    'SCHEMA': 'ahs_core.schema.schema'
}

INTERNAL_IPS = [
    '127.0.0.1',
]

# security related stuff
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_HTTPONLY = True
CORS_ORIGIN_ALLOW_ALL = True
SECURE_CONTENT_TYPE_NOSNIFF = False

hostname, _, ips = gethostbyname_ex(gethostname())
ipl = [ip[: ip.rfind(".")] + ".1" for ip in ips]
INTERNAL_IPS += ipl
ALLOWED_HOSTS += [hostname, '0.0.0.0', 'localhost'] + ipl
