from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from products.models import Product


class FeaturedProduct(models.Model):
    """Model for time-bound product promotion slots."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    display_order = models.PositiveIntegerField(default=0)

    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f'Featured: {self.product.name}'

    def clean(self):
        super().clean()
        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({'ends_at': 'End time must be after start time.'})

    @property
    def is_currently_active(self):
        now = timezone.now()
        if self.starts_at > now:
            return False
        return not self.ends_at or self.ends_at >= now
