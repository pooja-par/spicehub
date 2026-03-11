from django import forms
from django.core.exceptions import ValidationError

from django.db.utils import OperationalError, ProgrammingError
from .models import Product, Category

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            categories = Category.objects.all()
            friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        except (OperationalError, ProgrammingError):
            friendly_names = []

        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

    def clean_price_per_kg(self):
        """Ensure products cannot be saved with a free or negative price."""
        price_per_kg = self.cleaned_data['price_per_kg']
        if price_per_kg <= 0:
            raise ValidationError('Price per kg must be greater than 0.')
        return price_per_kg