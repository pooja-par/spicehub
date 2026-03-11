from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Product, Category

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'category',
        'price_per_kg',
        'stock',
        'image_preview',
    )
    ordering = ('name',)
    
    # Add a custom method to display image preview in list view
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="https://res.cloudinary.com/demo/image/upload/c_fill,h_50,w_50/{obj.image}" style="height: 50px;" />')
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)