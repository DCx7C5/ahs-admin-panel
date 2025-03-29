import logging
import warnings
from importlib import import_module
from typing import Any

from django.conf import settings
from django.apps import apps as django_apps
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
    user_logged_in,
    user_login_failed,
    _get_compatible_backends, # noqa
    _clean_credentials,  # noqa
    _get_backend_from_user,  # noqa
    _get_user_session_key,  # noqa
    _aget_user_session_key,  # noqa
    user_logged_out
)
from django.contrib.auth.base_user import AbstractBaseUser

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.middleware.csrf import rotate_token
from django.utils.crypto import constant_time_compare
from django.utils.deprecation import RemovedInDjango61Warning
from django.views.decorators.debug import sensitive_variables


User = get_user_model()
logger = logging.getLogger(__name__)



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


@sensitive_variables("credentials")
def authenticate(request=None, **credentials):
    """
    If the given credentials are valid, return a User object.
    """
    for backend, backend_path in _get_compatible_backends(request, **credentials):
        try:
            user = backend.authenticate(request, **credentials)
        except PermissionDenied:
            # This backend says to stop in our tracks - this user should not be
            # allowed in at all.
            break
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = backend_path
        return user

    # The credentials supplied are invalid to all backends, fire signal
    user_login_failed.send(
        sender=__name__, credentials=_clean_credentials(credentials), request=request
    )


@sensitive_variables("credentials")
async def aauthenticate(request=None, **credentials):
    """See authenticate()."""
    for backend, backend_path in _get_compatible_backends(request, **credentials):
        try:
            user = await backend.aauthenticate(request, **credentials)
        except PermissionDenied:
            # This backend says to stop in our tracks - this user should not be
            # allowed in at all.
            break
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = backend_path
        return user

    # The credentials supplied are invalid to all backends, fire signal.
    await user_login_failed.asend(
        sender=__name__, credentials=_clean_credentials(credentials), request=request
    )


def login(request, user, backend=None):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request. Note that data set during
    the anonymous session is retained when the user logs in.
    """
    # RemovedInDjango61Warning: When the deprecation ends, replace with:
    # session_auth_hash = user.get_session_auth_hash()
    session_auth_hash = ""
    # RemovedInDjango61Warning.
    if user is None:
        user = request.user
        warnings.warn(
            "Fallback to request.user when user is None will be removed.",
            RemovedInDjango61Warning,
            stacklevel=2,
        )

    # RemovedInDjango61Warning.
    if hasattr(user, "get_session_auth_hash"):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if _get_user_session_key(request) != user.pk or (
            session_auth_hash
            and not constant_time_compare(
                request.session.get(HASH_SESSION_KEY, ""), session_auth_hash
            )
        ):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()

    backend = _get_backend_from_user(user=user, backend=backend)

    request.session[SESSION_KEY] = user._meta.pk.value_to_string(user)  # noqa
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, "user"):
        request.user = user
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


async def alogin(request, user, backend=None):
    """See login()."""
    # RemovedInDjango61Warning: When the deprecation ends, replace with:
    # session_auth_hash = user.get_session_auth_hash()
    session_auth_hash = ""
    # RemovedInDjango61Warning.
    if user is None:
        warnings.warn(
            "Fallback to request.user when user is None will be removed.",
            RemovedInDjango61Warning,
            stacklevel=2,
        )
        user = await request.get_acached_user()
    # RemovedInDjango61Warning.
    if hasattr(user, "get_session_auth_hash"):
        session_auth_hash = user.get_session_auth_hash()

    if await request.session.ahas_key(SESSION_KEY):
        if await _aget_user_session_key(request) != user.pk or (
            session_auth_hash
            and not constant_time_compare(
                await request.session.aget(HASH_SESSION_KEY, ""),
                session_auth_hash,
            )
        ):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            await request.session.aflush()
    else:
        await request.session.acycle_key()

    backend = _get_backend_from_user(user=user, backend=backend)

    await request.session.aset(SESSION_KEY, user._meta.pk.value_to_string(user))
    await request.session.aset(BACKEND_SESSION_KEY, backend)
    await request.session.aset(HASH_SESSION_KEY, session_auth_hash)
    if hasattr(request, "user"):
        request.user = user
    rotate_token(request)
    await user_logged_in.asend(sender=user.__class__, request=request, user=user)


def logout(request):
    """
    Remove the authenticated user's ID from the request and flush their session
    data.
    """
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", True):
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)
    request.session.flush()
    if hasattr(request, "user"):
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()


async def alogout(request):
    """See logout()."""
    # Dispatch the signal before the user is logged out so the receivers have a
    # chance to find out *who* logged out.
    user = getattr(request, "auser", None)
    if user is not None:
        user = await user()
    if not getattr(user, "is_authenticated", True):
        user = None
    await user_logged_out.asend(sender=user.__class__, request=request, user=user)
    await request.session.aflush()
    if hasattr(request, "user"):
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()


def get_user_from_token_request(request) -> AbstractBaseUser | AnonymousUser:
    """
    Get user from request using token authentication.

    This function retrieves the user based on the authentication token
    and associated session. It falls back to AnonymousUser if no
    valid authenticated user is found.
    """

    # Get the auth payload from the token middleware
    auth_payload = getattr(request.token, "payload", None)
    if not auth_payload:
        request._cached_user = AnonymousUser()
        return request._cached_user  # noqa

    # Get the user ID from the payload
    user_id = auth_payload.get("user_id")
    if not user_id:
        request._cached_user = AnonymousUser()
        return request._cached_user  # noqa

    # Get session key from payload
    session_key = auth_payload.get("sess_id")

    try:
        # Try to get the user from the database
        user = User.objects.get(pk=user_id)

        # Verify if user is active
        if not user.is_active:
            request._cached_user = AnonymousUser()
            return request._cached_user  # noqa

        # If we have a session key, attach session data to user
        if session_key and hasattr(request, "session"):
            # Additional session verification could go here
            pass

        # Cache the user on the request for subsequent calls
        request._cached_user = user
        return user

    except User.DoesNotExist:
        logger.warning(
            f"Failed to retrieve user with ID {user_id} from token payload."
        )
        request._cached_user = AnonymousUser()
        return request._cached_user  # noqa


async def aget_user_from_token_request(request) -> AbstractBaseUser | AnonymousUser:
    """
    Async version of get_user_from_token_request.

    This function asynchronously retrieves the user based on the
    authentication token and associated session. Falls back to
    AnonymousUser if no valid authenticated user is found.
    """

    # Get the auth payload from the token middleware
    auth_payload = getattr(request.token, "payload", None)
    if not auth_payload:
        request._acached_user = AnonymousUser()
        return request._acached_user  # noqa

    # Get the user ID from the payload
    user_id = auth_payload.get("user_id")
    if not user_id:
        request._acached_user = AnonymousUser()
        return request._acached_user  # noqa

    # Get session key from payload
    session_key = auth_payload.get("sess_id")

    try:
        # Try to get the user from the database asynchronously
        user = await User.objects.aget(pk=user_id)

        # Verify if user is active
        if not user.is_active:
            request._acached_user = AnonymousUser()
            return request._acached_user  # noqa

        # If we have a session key, attach session data to user
        if session_key and hasattr(request, "session"):
            # You could verify the session is valid here
            # Example: await verify_session_validity(session_key, user_id)
            pass

        # Cache the user on the request for subsequent calls
        request._acached_user = user
        return user

    except User.DoesNotExist:
        logger.warning(
            f"Failed to retrieve user with ID {user_id} from token payload."
        )
        request._acached_user = AnonymousUser()
        return request._acached_user  # noqa


class TokenAuthentication:
    """
    DRF compatible token authentication class that works with AHSSessionToken.
    """

    def authenticate(self, request) -> tuple[AbstractBaseUser | AnonymousUser, Any | None] | None:
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        user = get_user_from_token_request(request)
        if user:
            return user, getattr(request, "token", None)
        return None

    async def aauthenticate(self, request) -> tuple[AbstractBaseUser | AnonymousUser, Any | None] | None:
        """
        Asynchronously authenticate the request and return a two-tuple of (user, token).
        """
        user = await aget_user_from_token_request(request)
        if user:
            return user, getattr(request, "token", None)
        return None
