from adrf.routers import DefaultRouter
from django.urls import path, include

from backend.api.views import ApiHostsView, get_user_data, \
    MenuItemViewSet, MenuItemsView
from backend.bookmarks.views import BookmarksCategoryView, BookmarksView

app_name = 'api'

router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')

urlpatterns = [
    path('hosts/', ApiHostsView.as_view(), name='hosts_list'),
    path('user/', get_user_data, name='user_data'),
    path('menu/', MenuItemsView.as_view(), name='menu'),
    path('bookmark/', BookmarksView.as_view(), name='bookmarks'),
    path('bookmark/category/', BookmarksCategoryView.as_view(), name='bookmarks_category'),
    path('', include(router.urls)),
]
