from django.db.utils import OperationalError, ProgrammingError

from .models import FeaturedProduct
def featured_products(request):
    """Return featured products for global template access.

    During first boot or partial migrations, the table may not exist yet.
    In that case, fail gracefully so the site stays up instead of returning 500.
    """
    try:
        featured = FeaturedProduct.objects.select_related('product')[:3]
        products = [fp.product for fp in featured]
    except (OperationalError, ProgrammingError):
        products = []

    return {'featured_products': products}