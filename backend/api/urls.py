from adrf.routers import DefaultRouter
from django.urls import path, include

from backend.api.views import (
    ApiHostsView,
    get_user_data,
    MenuItemViewSet,
    MenuItemsView,
)

app_name = 'api'

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')

urlpatterns = [
    path('hosts/', ApiHostsView.as_view(), name='hosts_list'),
    path('user/', get_user_data, name='user_data'),
    path('menu/', MenuItemsView.as_view(), name='menu'),
    path('', include(router.urls)),
]
