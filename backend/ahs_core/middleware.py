from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.contrib.auth import get_user_model
from django.core.handlers.asgi import ASGIRequest
from django.contrib.auth import aget_user

from backend.ahs_accounts.serializers import AHSUserSerializer
from backend.ahs_endpoints.models import EndPoint
from backend.ahs_endpoints.serializers import EndPointSerializer

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
            response.context_data["AHS_USER"] = await AHSUserSerializer(user).adata

        await self.get_pages_data(response)
        return response

    @staticmethod
    async def get_pages_data(response):
        response.context_data["PAGES"] = []
        async for item in EndPoint.objects.all():
            response.context_data["PAGES"].append(await EndPointSerializer(item).adata)


