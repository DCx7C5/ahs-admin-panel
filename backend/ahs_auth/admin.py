from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.urls import path


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
        js = ('admin/js/addSuperUserWebAuthn.js',)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        """
        Extends the default method to add custom context to the change form.
        """
        if obj.is_superuser and not obj.available_auth.filter(name="webauthn").exists():
            context.update({
                "webauthn_username": obj.username,
                "webauthn_useruid": f"{obj.uid}",
            })

        # Call the parent method with updated context
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/add_webauthn/', self.admin_site.admin_view(self.add_webauthn), name='add_webauthn'),
        ]
        return custom_urls + urls

    def add_webauthn(self, request, object_id, form_url='', extra_context=None):
        return self.response_change(request, obj=User.objects.get(pk=object_id))



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
