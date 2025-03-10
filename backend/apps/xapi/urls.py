from django.urls import path

from backend.ahs_core.views import default_view

app_name = 'xapi'

urlpatterns = [
    path('ahs_settings/', default_view, name='ahs_settings'),
    path('', default_view, name='stats'),
]

