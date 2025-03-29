
from django.urls import path, include
from backend.ahs_core.views import default_view

app_name = 'ahs_core'

urlpatterns = [
    path('accounts/signup/', default_view, name='signup'),
    path('accounts/login/', default_view, name='login'),
    path('test/', default_view, name='test'),
    path('test2/', default_view, name='test2'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', default_view, name='dashboard'),
    path('settings/', default_view, name='settings'),
    path('', default_view, name='default'),
]

