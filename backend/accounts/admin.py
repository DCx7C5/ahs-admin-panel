from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from backend.accounts.forms import CustomUserCreationForm, CustomUserChangeForm

AHSUser = get_user_model()


class AHSUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = AHSUser


    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image',)}),
    )
    show_full_result_count = True



admin.site.register(AHSUser, AHSUserAdmin)
