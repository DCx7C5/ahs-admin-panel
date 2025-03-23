
from django.urls import path, include
from backend.ahs_core.views import default_view, signup_view, login_view

app_name = 'ahs_core'

urlpatterns = [
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/login/', login_view, name='login'),
    path('test/', default_view, name='test'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', default_view, name='dashboard'),
    path('settings/', default_view, name='settings'),
    path('', default_view, name='default'),
]

