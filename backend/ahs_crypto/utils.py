import importlib
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_ecc_backend():
    module_path, class_name = settings.ECC_BACKEND.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)

        ecc_backend_class = getattr(module, class_name)

        return ecc_backend_class
    except (ImportError, AttributeError) as ex:
        raise ImportError(f"Error importing '{settings.ECC_BACKEND}': {ex}")


def validate_backend(backend_string: str) -> bool:
    module_path, class_name = backend_string.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
        return hasattr(module, class_name)
    except (ImportError, AttributeError) as ex:
        raise ImportError(f"Error importing '{settings.ECC_BACKEND}': {ex}")


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
