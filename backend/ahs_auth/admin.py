import secrets

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from webauthn import generate_registration_options, options_to_json
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from backend.ahs_auth.models import WebAuthnCredential, AuthMethod


User = get_user_model()


@admin.register(User)
class AHSUserAdmin(UserAdmin):
    model = User
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image',)}),
    )
    show_full_result_count = True

    class Media:
        ts = ('admin/js/addSuperUserWebAuthn.ts',)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        """
        Extends the default method to add custom context to the change form.
        """
        if obj.pk != 1:
            return super().render_change_form(request, context, add, change, form_url, obj)

        # Generate custom data (e.g., WebAuthn-specific information)
        challenge = secrets.token_bytes(128).hex()

        user_id = f"{obj.uid}"
        username = obj.username

        options: PublicKeyCredentialCreationOptions = generate_registration_options(
            rp_name=settings.SITE_NAME,
            rp_id=request.get_host(),
            user_id=user_id.encode('utf-8'),
            user_name=username,
            user_display_name=username,
            challenge=challenge.encode('utf-8'),
            timeout=60000,
            exclude_credentials=[],
            supported_pub_key_algs=[COSEAlgorithmIdentifier(-7),
                                    COSEAlgorithmIdentifier(-8),
                                    COSEAlgorithmIdentifier(-257)],
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=AuthenticatorSelectionCriteria(
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
        )

        json_options = options_to_json(options=options)

        # Add the custom options and data to the context passed to the template
        context.update({
            "webauthn_options": json_options,  # Dynamic data for WebAuthn
        })

        # Call the parent method with updated context
        return super().render_change_form(request, context, add, change, form_url, obj)

    def add_webauthn(self):
        pass


@admin.register(AuthMethod)
class AuthMethodAdmin(admin.ModelAdmin):
    model = AuthMethod


@admin.register(WebAuthnCredential)
class WebAuthnCredentialAdmin(admin.ModelAdmin):
    model = WebAuthnCredential
    list_display = ('user', 'credential_type', 'device_type', 'sign_count')
    list_filter = ('user', 'credential_type', 'device_type')
    search_fields = ('user__username', 'user__uid')
    ordering = ('user', 'credential_type', 'device_type')
    actions = ['delete_selected']
