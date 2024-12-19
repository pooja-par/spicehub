from django.db import models


class Category(models.Model):
    """
    Model representing a category of products.
    """
    name = models.CharField(max_length=254, unique=True)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """
    Model representing a product.
    """
    category = models.ForeignKey(
        'Category',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products'
    )
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price_per_kg = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to='media/')
    #json_data = models.JSONField(default=dict)  # Additional metadata (e.g., origin, grade)

    def __str__(self):
        return self.name
