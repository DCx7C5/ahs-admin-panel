from django.urls import path

from backend.core.views import async_dashboard_view

app_name = 'xapi'

urlpatterns = [
    path('settings/', async_dashboard_view, name='settings'),
    path('', async_dashboard_view, name='stats'),
]

