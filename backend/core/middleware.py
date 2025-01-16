import logging

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth import get_user_model
from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import aget_user

from backend.api.serializers import AHSUserSerializer, MenuItemSerializer
from backend.core.models import MenuItem

AHSUser = get_user_model()


class AHSMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request: ASGIRequest):
        return await self.get_response(request)

    async def process_template_response(self, request, response):
        if not hasattr(request, '_cached_user'):
            request._cached_user = await aget_user(request)
        await self.get_menu_data(response)
        await self.get_user_data(request, response)
        await self.create_urls(request, response)
        return response

    @staticmethod
    async def get_user_data(request, response):
        user = request._cached_user  # noqa
        if user.is_authenticated:
            response.context_data["AHS_SERIAL_USER"] = await AHSUserSerializer(user).adata

    @staticmethod
    async def get_menu_data(response):
        response.context_data["MENU_ITEMS"] = []
        async for item in MenuItem.objects.all():
            response.context_data["MENU_ITEMS"].append(await MenuItemSerializer(item).adata)

    @staticmethod
    async def create_urls(request, response):
        func = request.build_absolute_uri
        response.context_data['ABSOLUTE_ROOT'] = func('/')[:-1].strip('/')
        response.context_data['ABSOLUTE_ROOT_URL'] = func('/').strip('/')
        response.context_data['FULL_URL_INCL_PATH'] = func()
        response.context_data['FULL_URL'] = func('?')
