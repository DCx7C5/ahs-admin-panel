from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class AHSUserAdmin(UserAdmin):
    model = User
    fieldsets = tuple(tuple(
        (section[0], {"fields": tuple(field if field != "email" else "public_key" for field in section[1]["fields"])})
        for
        section in UserAdmin.fieldsets))

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('image',)}),
    )
    list_display = tuple(field if field != "email" else "public_key" for field in UserAdmin.list_display)
    search_fields = tuple(field if field != "email" else "public_key" for field in UserAdmin.search_fields)
    show_full_result_count = True
