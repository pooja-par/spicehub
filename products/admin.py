from django.contrib import admin
from django import forms

from .models import Product, Category
from .widgets import CloudinarySelectWidget

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "image": CloudinarySelectWidget(),
        }

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'name',
        'slug',
        'category',
        'price_per_kg',
        'stock',
        'image',
    )
    ordering = ('name',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
