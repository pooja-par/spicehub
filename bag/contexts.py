from decimal import Decimal

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from products.models import Product


def bag_contents(request):
    """Context processor to make shopping bag totals globally available.

    During first boot or transient database errors, fail gracefully and return
    an empty bag context instead of raising a 500 on every page render.
    """
    empty_context = {
        'bag_items': [],
        'bag_total': Decimal('0.00'),
        'product_count': 0,
        'delivery': Decimal('0.00'),
        'free_delivery_delta': Decimal(str(settings.FREE_DELIVERY_THRESHOLD)),
        'grand_total': Decimal('0.00'),
    }

    try:
        bag = request.session.get('bag', {})
    except Exception:
        # If session backend/table is not ready yet, keep rendering pages.
        return empty_context

    bag_items = []
    total = Decimal('0.00')
    product_count = 0

    try:
        product_ids = bag.keys()
        products = Product.objects.filter(pk__in=product_ids)
        product_map = {str(product.id): product for product in products}
    except (OperationalError, ProgrammingError):
        return empty_context

    for product_id, quantity in bag.items():
        product = product_map.get(str(product_id))
        if product:
            quantity = Decimal(str(quantity))
            pricing = product.get_pricing_for_quantity(quantity)

            bag_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': pricing['subtotal'],
                'base_subtotal': pricing['base_subtotal'],
                'discount_percent': pricing['discount_percent'],
                'discounted_unit_price': pricing['discounted_unit_price'],
                'savings': pricing['savings'],
            })
            total += pricing['subtotal']
            product_count += quantity

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100) * 2
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')

    grand_total = total + delivery

    return {
        'bag_items': bag_items,
        'bag_total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
    }