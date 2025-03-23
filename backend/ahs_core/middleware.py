import logging
import time
from functools import partial
from importlib import import_module

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.middleware import auser
from django.contrib.messages.storage import default_storage
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import HttpRequest, HttpResponse
from django.middleware.csrf import rotate_token
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.utils.http import http_date

logger = logging.getLogger(__name__)

User = get_user_model()


class AHSAdminPanelMiddleware(MiddlewareMixin):
    """
    Manages sessions, session authentication and messages for the /admin backend
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
        # auth
        logger.debug("process_request auth")
        request.user = SimpleLazyObject(lambda: get_user(request))  # noqa
        request.auser = partial(auser, request)
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


class AHSSessionTokenMiddleware(MiddlewareMixin):
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        super().__init__(get_response)
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    async def __call__(self, request: HttpRequest):
        await self.process_request(request)
        response = await self.get_response(request)
        response = await self.process_response(request, response)
        return response

    async def process_request(self, request: HttpRequest) -> None:
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        request.session = self.SessionStore(session_key)
        logger.debug(f"process_request headers {request.headers}")
        logger.debug(f"process_request cookies {request.COOKIES}")
        logger.debug(f"process_request META {request.META}")

    async def process_response(self, request, response) -> HttpResponse:
        return response

