import secrets
import uuid

from django.core.cache import cache
from requests import post
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser
from django.http import HttpResponseRedirect
from django.urls import path
from webauthn import generate_registration_options, options_to_json
from webauthn.helpers.structs import PublicKeyCredentialCreationOptions, AttestationConveyancePreference, \
    AuthenticatorSelectionCriteria, AuthenticatorAttachment, UserVerificationRequirement

from backend.ahs_auth.models import WebAuthnCredential
from backend.ahs_auth.webauthn import EXPECTED_RP_ID, SUPPORTED_ALGOS

User = get_user_model()


@admin.register(User)
class AHSUserAdmin(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image',)}),
    )
    show_full_result_count = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/add_webauthn_registration/',
                 self.admin_site.admin_view(self.add_webauthn_registration),
                 name='add_webauthn'),
        ]
        return custom_urls + urls

    def add_webauthn_registration(self, request, object_id, **kwargs):
        username = ''
        user_id = None
        user: User | AbstractUser = self.get_object(request, object_id)
        if user:
            username = user.username  # Get the username
            user_id = getattr(user, 'uid', f'{uuid.uuid4()}')

        challenge = secrets.token_urlsafe(128)
        random = secrets.token_hex(32)
        options: PublicKeyCredentialCreationOptions = generate_registration_options(
            rp_name=settings.SITE_NAME,
            rp_id=EXPECTED_RP_ID,
            user_id=f"{user_id}".encode('utf-8'),
            user_name=username,
            user_display_name=username,
            challenge=challenge.encode('utf-8'),
            timeout=60000,
            supported_pub_key_algs=SUPPORTED_ALGOS,
            attestation=AttestationConveyancePreference.DIRECT,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                user_verification=UserVerificationRequirement.REQUIRED,
            ),
        )
        json_options = options_to_json(options=options)
        cache.set(f"{random}", f"{challenge}.|.{username}.|.{user_id}", 600)

        host = request.get_host()
        response = post(
            f'https://{host}/api/auth/webauthn/register/verify/',
            data={'random': random, 'credential': json_options},
            headers={'Content-Type': 'application/json'},
        )
        return HttpResponseRedirect(request.path)

    add_webauthn_registration.short_description = "Add WebAuthn Registration to a manually added user"


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    model = WebAuthnCredential
    list_display = ('user', 'credential_type', 'device_type', 'sign_count')
    list_filter = ('user', 'credential_type', 'device_type')
    search_fields = ('user__username', 'user__uid')
    ordering = ('user', 'credential_type', 'device_type')
    actions = ['delete_selected']
