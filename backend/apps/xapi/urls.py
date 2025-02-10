from django.urls import path

from backend.ahs_core.views import async_dashboard_view

app_name = 'xapi'

urlpatterns = [
    path('ahs_settings/', async_dashboard_view, name='ahs_settings'),
    path('', async_dashboard_view, name='stats'),
]

