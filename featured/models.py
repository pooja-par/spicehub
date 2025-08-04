from django.db import models
from products.models import Product

class FeaturedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
