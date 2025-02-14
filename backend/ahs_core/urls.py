from django.urls import path, include

from backend.ahs_core.views import UserProfileView, async_dashboard_view, ReactView

app_name = 'ahs_core'


urlpatterns = [
    path('ahs_settings/', async_dashboard_view, name='ahs_settings'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('xapi/', include('backend.apps.xapi.urls'), name='xapi'),
    path('', async_dashboard_view, name='dashboard'),
    path('dashboard/', async_dashboard_view, name='dashboard'),
    path('api/', include('backend.ahs_api.urls'), name='api'),
    path('api-auth/', include('rest_framework.urls')),
]

