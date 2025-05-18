from django.contrib import admin
from .models import CustomUser
from .models import Job


class CustomUserAdmin(admin.ModelAdmin):
    # Specify which fields to display in the admin list view
    list_display = (
    'email', 'full_name', 'phone_number', 'education_level', 'job_preference', 'industry_interest', 'resume',
    'skills', 'is_active', 'is_staff')

    # Add ordering to sort the results
    ordering = ('email',)

    # Add fields to filter by in the admin interface
    list_filter = ('is_staff', 'is_active')

    # Add search functionality
    search_fields = ('email', 'full_name')

    # Define fields to display in the form view
    fieldsets = (
        (None, {
            'fields': (
            'email', 'full_name', 'phone_number', 'education_level', 'job_preference', 'industry_interest', 'resume')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'full_name', 'phone_number', 'education_level', 'job_preference', 'industry_interest', 'resume',
            'password1', 'password2'),
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)

class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_date')  # Change fields as per your Job model
    search_fields = ('title', 'company')
    list_filter = ('industry', 'location')  # Adjust according to your model fields

admin.site.register(Job, JobAdmin)
