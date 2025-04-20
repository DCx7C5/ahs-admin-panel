from django.urls import path

from backend.ahs_auth.views import webauthn_authentication_view, webauthn_register_view, \
    webauthn_verify_registration_view, webauthn_verify_authentication_view

app_name = 'auth'

urlpatterns = [
    path('webauthn/', webauthn_authentication_view, name='webauthn_auth'),
    path('webauthn/verify/', webauthn_verify_authentication_view, name='webauthn_verify_auth'),
    path('webauthn/register/', webauthn_register_view, name='webauthn_reg'),
    path('webauthn/register/verify/', webauthn_verify_registration_view, name='webauthn_verify_reg'),
]

