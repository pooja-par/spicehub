from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

from .models import FeaturedProduct
def featured_products(request):
    """Return currently active featured products for global template access."""
    try:
        #featured = FeaturedProduct.objects.select_related('product')[:3]
        now = timezone.now()
        featured = FeaturedProduct.objects.select_related('product').filter(
            starts_at__lte=now,
        ).filter(
            ends_at__isnull=True,
        ) | FeaturedProduct.objects.select_related('product').filter(
            starts_at__lte=now,
            ends_at__gte=now,
        )
        featured = featured.order_by('display_order')[:3]
        products = [fp.product for fp in featured]
    except (OperationalError, ProgrammingError):
        products = []

    return {'featured_products': products}