from django.db import models
from products.models import Product

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    session_id = models.CharField(max_length=255)

    def subtotal(self):
        return self.product.price_per_kg * self.quantity


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    json_data = models.JSONField(default=dict)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"
