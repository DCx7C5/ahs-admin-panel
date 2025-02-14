from datetime import timedelta
from os import environ
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('SECRET_KEY')

INSTALLED_APPS = [
    # ASGI Server
    'hypercorn',
    'daphne',

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
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'adrf',

    'corsheaders',

    # webpack loader
    'webpack_loader',

    # Toolbar Plugins/Modules
    'debug_toolbar',
    'graphene_django',

    # Core Apps
    'backend.ahs_crypto',
    'backend.ahs_accounts',
    'backend.ahs_api',

    'backend.ahs_core',
    'backend.ahs_channels',
    'backend.ahs_endpoints',
    'backend.ahs_settings',
    'backend.ahs_socket_conns',
    'backend.ahs_tasks',
    'backend.ahs_workers',

    # Apps / Plugins
    'backend.apps',
    'backend.apps.bookmarks',
    'backend.apps.network',
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

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

SITE_NAME = 'AHSAdminPanel'



MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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


# REST API and Token Auth
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ROTATE_REFRESH_TOKENS = True

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

LOGIN_REDIRECT_URL = 'ahs_core:dashboard'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

AUTH_USER_MODEL = "ahs_accounts.AHSUser"

INTERNAL_IPS = [
    '127.0.0.1',
]

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]

SESSION_ENGINE = 'django.contrib.sessions.backends.db'


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]


BLACKLIST_AFTER_ROTATION = True
ALGORITHM = "ES521"

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'SIGNING_KEY': None,
    'VERIFYING_KEY': None,

    "AUTH_HEADER_TYPES": ("Bearer",),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'ALGORITHM': 'ES521',

}
