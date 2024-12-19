from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile

# Register the UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'user__email', 'phone_number')
