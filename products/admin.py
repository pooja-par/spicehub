from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
import cloudinary
import cloudinary.api
from cloudinary.exceptions import Error as CloudinaryError
import logging

from .models import Product, Category

logger = logging.getLogger(__name__)

class CloudinaryImageSelectWidget(forms.Select):
    """Widget that displays Cloudinary images with preview"""
    
    def __init__(self, attrs=None):
        choices = self.get_cloudinary_images()
        super().__init__(attrs=attrs, choices=choices)
    
    def get_cloudinary_images(self):
        """Fetch images from Cloudinary"""
        try:
            response = cloudinary.api.resources(type="upload", max_results=100)
            resources = response.get("resources", [])
            return [(r["public_id"], r["public_id"]) for r in resources]
        except CloudinaryError as err:
            logger.exception("Cloudinary API error: %s", err)
            return [("", "Error loading images")]
        except Exception as err:
            logger.exception("Unexpected error while loading Cloudinary images: %s", err)
            return [("", "Error loading images")]
    
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        
        # Render the select dropdown
        select_html = super().render(name, value, attrs, renderer)
        output.append(select_html)
        
        # Add image preview if a value is selected
        if value:
            preview_url = f"https://res.cloudinary.com/demo/image/upload/c_fill,h_150,w_150/{value}"
            output.append(
                f'<div style="margin-top: 10px;">'
                f'<img src="{preview_url}" alt="Preview" style="max-width: 150px; max-height: 150px; border: 1px solid #ddd; padding: 5px;"/>'
                f'</div>'
            )
        
        # Add refresh button with inline JavaScript
        output.append(
            f'<div style="margin-top: 10px;">'
            f'<button type="button" onclick="location.reload();" style="background: #417690; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">'
            f'Refresh Images'
            f'</button>'
            f'</div>'
        )
        
        return mark_safe(''.join(output))

class ProductAdminForm(forms.ModelForm):
    # Use a CharField for the image instead of the default field
    image = forms.CharField(
        widget=CloudinaryImageSelectWidget(),
        required=False,
        help_text="Select an image from Cloudinary"
    )
    
    class Meta:
        model = Product
        fields = "__all__"

class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
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