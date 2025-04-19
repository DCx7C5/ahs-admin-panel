from django.urls import path

from backend.ahs_auth.views import webauthn_authentication_view, webauthn_register_view, webauthn_verify_view

app_name = 'auth'

urlpatterns = [
    path('webauthn/', webauthn_authentication_view, name='webauthn_authenticate'),
    path('webauthn/register/', webauthn_register_view, name='webauthn_register'),
    path('webauthn/verify/', webauthn_verify_view, name='webauthn_authenticate_verify'),
]

