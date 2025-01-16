from django.urls import path, include
from backend.core.views import UserProfileView, async_dashboard_view, ReactView

app_name = 'core'


urlpatterns = [
    path('settings/', async_dashboard_view, name='settings'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='profile'),
    path('xapi/', include('backend.xapi.urls'), name='xapi'),
    path('', async_dashboard_view, name='dashboard'),
    path('dashboard/', async_dashboard_view, name='dashboard'),
]

