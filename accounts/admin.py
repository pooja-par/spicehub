from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile

# Inline UserProfile in the User admin interface
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

# Re-register User with the custom admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register UserProfile separately for individual management
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'user__email', 'phone_number')
