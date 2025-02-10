import importlib

from django.core.exceptions import ImproperlyConfigured
from django.apps import apps as django_apps

from .settings import validate_settings, ECC_BACKEND

validate_settings()

def get_ecc_backend():
    """
    Dynamically import the ECC backend class specified by the ECC_BACKEND setting
    and return an instance of that class.
    """

    module_path, class_name = ECC_BACKEND.rsplit(".", 1)

    try:
        module = importlib.import_module(module_path)

        ecc_backend_class = getattr(module, class_name)

        return ecc_backend_class
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Error importing '{ECC_BACKEND}': {e}")


def get_public_key_model():
    try:
        return django_apps.get_model(
            settings.ECC_PRIVKEY_MODEL.replace("PrivateKey", "PublicKey"),
            require_ready=False,
        )

    except ValueError:
        raise ImproperlyConfigured(
            "ECC_PUBKEY_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "ECC_PUBKEY_MODEL refers to model '%s' that has not been installed"
            % settings.ECC_PRIVKEY_MODEL
        )

def get_private_key_model():
    """
    Return the asymmetric key models (PrivateKey and PublicKey) used in this project.
    """
    try:
        return django_apps.get_model(
            settings.ECC_PRIVKEY_MODEL,
            require_ready=False,
        )

    except ValueError:
        raise ImproperlyConfigured(
            "ECC_PRIVKEY_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "ECC_PRIVKEY_MODEL refers to model '%s' that has not been installed"
            % settings.ECC_PRIVKEY_MODEL
        )
