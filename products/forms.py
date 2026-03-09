from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

    def clean_price_per_kg(self):
        """Ensure products cannot be saved with a free or negative price."""
        price_per_kg = self.cleaned_data['price_per_kg']
        if price_per_kg <= 0:
            raise ValidationError('Price per kg must be greater than 0.')
        return price_per_kg

    def clean(self):
        """Generate a slug from the product name when one is not supplied."""
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        name = cleaned_data.get('name')

        if not slug and name:
            cleaned_data['slug'] = slugify(name)

        return cleaned_data