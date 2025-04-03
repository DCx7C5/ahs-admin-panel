from importlib import import_module

from django.conf import settings
from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured


def get_ahs_session_store():
    """
    Return the AHS session engine.
    """
    return import_module(settings.SESSION_ENGINE_AHS).SessionStore


def get_ahs_session_model():
    """
    Return the AHS session model.
    """

    try:
        return django_apps.get_model(
            settings.SESSION_MODEL_AHS,
            require_ready=False
        )
    except ValueError:
        raise ImproperlyConfigured(
            "SESSION_MODEL_AHS must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "SESSION_MODEL_AHS refers to model '%s' that has not been installed"
            % settings.AUTH_USER_MODEL
        )
