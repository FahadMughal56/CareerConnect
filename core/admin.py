from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Job


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('skills', 'experience_level')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('skills', 'experience_level')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)


admin.site.register(Job)