import logging
import time
from functools import partial
from importlib import import_module

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import HttpRequest, HttpResponse
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.http import http_date

from backend.ahs_core.auth import get_ahs_session_store, get_user_from_token_request, aget_user_from_token_request
from backend.ahs_core.token import AHSToken

logger = logging.getLogger(__name__)

User = get_user_model()
SessionStore = get_ahs_session_store()


def get_cached_user(request: HttpRequest) -> AnonymousUser | AbstractBaseUser:
    _cached_user = None
    if not hasattr(request, "_cached_user"):
        request._cached_user = get_user_from_token_request(request)
    return _cached_user  # noqa


async def get_acached_user(request: HttpRequest) -> AnonymousUser | AbstractBaseUser:
    _acached_user = None
    if not hasattr(request, "_acached_user"):
        request._acached_user = await aget_user_from_token_request(request)
    return _acached_user  # noqa


class AHSAdminPanelMiddleware(MiddlewareMixin):
    """
        Summarizes session, auth & messages middleware in one class and
        restricts usage to admin panel only.
    """
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        super().__init__(get_response)
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    async def __call__(self, request: HttpRequest):
        if not request.path.startswith('/admin/'):
            return await self.get_response(request)
        await self.process_request(request)
        response = await self.get_response(request)
        response = await self.process_response(request, response)
        return response

    async def process_request(self, request: HttpRequest) -> None:
        # session
        logger.debug("process_request session")
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)
        print(request.session)
        # auth
        logger.debug("process_request auth")
        request.user = SimpleLazyObject(lambda: get_cached_user(request))  # noqa
        request.auser = partial(get_acached_user, request)
        # messages
        logger.debug("process_request messages")
        request._messages = await sync_to_async(default_storage)(request)


    async def process_response(self, request, response) -> HttpResponse:
        # Messages
        logger.debug("process_response messages")

        if hasattr(request, "_messages"):
            unstored_messages = await sync_to_async(request._messages.update)(response)  # noqa
            if unstored_messages and settings.DEBUG:
                raise ValueError("Not all temporary messages could be stored.")
        # Session
        logger.debug("process_response Session")

        try:
            accessed = request.session.accessed
            modified = request.session.modified
            empty = request.session.is_empty()
        except AttributeError:
            return response
        # First check if we need to delete this cookie.
        # The session should be deleted only if the session is entirely empty.
        if settings.SESSION_COOKIE_NAME in request.COOKIES and empty:
            response.delete_cookie(
                settings.SESSION_COOKIE_NAME,
                path=settings.SESSION_COOKIE_PATH,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite=settings.SESSION_COOKIE_SAMESITE,
            )
            patch_vary_headers(response, ("Cookie",))
        else:
            if accessed:
                patch_vary_headers(response, ("Cookie",))
            if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                if await request.session.aget_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = await request.session.aget_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                # Save the session data and refresh the client cookie.
                # Skip session save for 5xx responses.
                if response.status_code < 500:
                    try:
                        await request.session.asave()
                    except UpdateError:
                        raise SessionInterrupted(
                            "The request's session was deleted before the "
                            "request completed. The user may have logged "
                            "out in a concurrent request, for example."
                        )
                    response.set_cookie(
                        settings.SESSION_COOKIE_NAME,
                        request.session.session_key,
                        max_age=max_age,
                        expires=expires,
                        domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None,
                        httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                        samesite=settings.SESSION_COOKIE_SAMESITE,
                    )
        return response


class AHSTokenMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        super().__init__(get_response)
        self.TokenStore = import_module(settings.AHS_TOKEN_ENGINE).AHSTokenStore

    async def __call__(self, request: HttpRequest):
        if request.path.startswith('/admin/'):
            return await self.get_response(request)
        await self.process_request(request)
        response = await self.get_response(request)
        response = await self.process_response(request, response)
        return response

    async def process_request(self, request: HttpRequest) -> None:
        token = request.headers.get('X-AHS-Token')
        request.token = AHSToken(token) if token else None

    async def process_response(self, request, response):

        return response


class AHSAuthenticationMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = False

    async def process_request(self, request: HttpRequest) -> None:
        if not hasattr(request, "token"):
            raise ImproperlyConfigured(
                "The AHS authentication middleware requires token "
                "middleware to be installed. Edit your MIDDLEWARE setting to "
                "insert "
                "'backend.ahs_core.middlewares.AHSTokenMiddleware' before "
                "'backend.ahs_core.middlewares.AHSAuthenticationMiddleware'."
            )
        request.user = SimpleLazyObject(lambda: get_cached_user(request))  # noqa
        request.auser = partial(get_acached_user, request)


class AHSMessagesMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = False
