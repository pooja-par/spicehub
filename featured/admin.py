from django.contrib import admin
from .models import FeaturedProduct

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'display_order')
