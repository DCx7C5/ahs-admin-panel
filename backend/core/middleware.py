from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth import get_user_model
from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import aget_user

from backend.core.serializers import AHSUserSerializer, MenuItemSerializer, SessionSocketUrlSerializer
from backend.core.models import AHSEndPoint
from backend.core.models.socket_url import SessionSocketURL

AHSUser = get_user_model()

class AHSMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request: ASGIRequest):
        return await self.get_response(request)

    async def process_template_response(self, request, response):
        if not hasattr(request, '_cached_user'):
            request._cached_user = await aget_user(request)

        user = request._cached_user  # noqa
        if user.is_authenticated:
            response.context_data["AHS_SERIAL_USER"] = await AHSUserSerializer(user).adata
            await self.add_socket_url(request, response)

        await self.get_menu_data(response)
        await self.create_urls(request, response)
        return response


    @staticmethod
    async def get_menu_data(response):
        response.context_data["MENU_ITEMS"] = []
        async for item in AHSEndPoint.objects.all():
            response.context_data["MENU_ITEMS"].append(await MenuItemSerializer(item).adata)

    @staticmethod
    async def create_urls(request, response):
        func = request.build_absolute_uri
        response.context_data['ABSOLUTE_ROOT'] = func('/')[:-1].strip('/')
        response.context_data['ABSOLUTE_ROOT_URL'] = func('/').strip('/')
        response.context_data['FULL_URL_INCL_PATH'] = func()
        response.context_data['FULL_URL'] = func('?')

    @staticmethod
    async def add_socket_url(request, response):
        surl = await SessionSocketURL.objects.get_url(request.session.session_key)
        response.context_data['SOCKET_URL'] = await SessionSocketUrlSerializer(surl).adata

