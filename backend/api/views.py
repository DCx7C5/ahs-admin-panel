import logging

from adrf.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.decorators import authentication_classes, api_view
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from adrf.views import APIView
from adrf.requests import Request
from backend.api.serializers import HostSerializer, AHSUserSerializer, MenuItemSerializer
from backend.core.models import MenuItem

logger = logging.getLogger(__name__)

AHSUser = get_user_model()


@authentication_classes([SessionAuthentication])
@api_view(http_method_names=['get'])
async def get_user_data(request: Request):
    user_data = await AHSUserSerializer(request.user).data
    return Response(user_data)


class ApiHostsView(APIView):
    permission_classes = [IsAuthenticated]
    view_is_async = True

    async def get(self, request: Request) -> Response:
        logger.debug(f'{self.view_is_async}')
        serializer = HostSerializer(data=request.data)
        serializer.is_valid()
        return Response(await serializer.adata)


class MenuItemsView(APIView):
    """
    API View to serve menu items to the React frontend.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MenuItemSerializer
    view_is_async = True
    queryset = MenuItem.objects.all()




class MenuItemViewSet(ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
