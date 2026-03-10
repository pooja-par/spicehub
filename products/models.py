from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


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

    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price_per_kg = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to='media/')
    #json_data = models.JSONField(default=dict)  # Additional metadata (e.g., origin, grade)
    low_stock_threshold = models.PositiveIntegerField(default=25, blank=True)
    critical_stock_threshold = models.PositiveIntegerField(default=5, blank=True)
    discount_rules = models.JSONField(
        default=list,
        blank=True,
        help_text='Optional list like [{"minimum_quantity": 5, "discount_rate": 0.05}]',
    )

    BULK_DISCOUNT_RULES = (
        (Decimal('20'), Decimal('0.15')),
        (Decimal('10'), Decimal('0.10')),
        (Decimal('5'), Decimal('0.05')),
    )

    def __str__(self):
        return self.name
    
    def clean(self):
        super().clean()
        if self.critical_stock_threshold >= self.low_stock_threshold:
            raise ValidationError({
                'critical_stock_threshold': 'Critical threshold must be lower than low-stock threshold.'
            })
        self._normalized_discount_rules()

    def save(self, *args, **kwargs):
        """Ensure each product has a slug, even for legacy/imported rows."""
        if not self.slug and self.name:
            base_slug = slugify(self.name) or "product"
            slug_candidate = base_slug
            suffix = 2
            while Product.objects.exclude(pk=self.pk).filter(slug=slug_candidate).exists():
                slug_candidate = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug_candidate
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        """Return a stock label that can be reused in views/templates."""
        if self.stock <= 0:
            return 'out_of_stock'
        if self.stock <= self.critical_stock_threshold:
            return 'critical_stock'
        if self.stock <= self.low_stock_threshold:
            return 'low_stock'
        return 'in_stock'

    def _normalized_discount_rules(self):
        """Return discount rules as sorted Decimal tuples and validate schema."""
        source_rules = self.discount_rules or [
            {
                'minimum_quantity': int(minimum_quantity),
                'discount_rate': float(discount_rate),
            }
            for minimum_quantity, discount_rate in self.BULK_DISCOUNT_RULES
        ]

        if not isinstance(source_rules, list):
            raise ValidationError({'discount_rules': 'Discount rules must be a list.'})

        normalized = []