from decimal import Decimal

from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError

from products.models import Product


DEFAULT_FREE_DELIVERY_THRESHOLD = Decimal('30')
DEFAULT_STANDARD_DELIVERY_PERCENTAGE = Decimal('10')


def bag_contents(request):
    """Context processor to make shopping bag totals globally available.

    During first boot or transient database errors, fail gracefully and return
    an empty bag context instead of raising a 500 on every page render.
    """
    free_delivery_threshold = Decimal(str(getattr(settings, 'FREE_DELIVERY_THRESHOLD', 30)))
    delivery_percentage = Decimal(str(getattr(settings, 'STANDARD_DELIVERY_PERCENTAGE', 0)))

    empty_context = {
        'bag_items': [],
        'bag_total': Decimal('0.00'),
        'product_count': 0,
        'delivery': Decimal('0.00'),
        'free_delivery_delta': free_delivery_threshold,
        'grand_total': Decimal('0.00'),
    }

    try:
        bag = request.session.get('bag', {})
    except Exception:
        # If session backend/table is not ready yet, keep rendering pages.
        return empty_context

    bag_items = []
    total = Decimal('0.00')
    product_count = Decimal('0.00')

    try:
        #product_ids = bag.keys()
        products = Product.objects.filter(pk__in=bag.keys())
        product_map = {str(product.id): product for product in products}
    except (OperationalError, ProgrammingError):
        return empty_context

    for product_id, quantity in bag.items():
        product = product_map.get(str(product_id))
        if not product:
            continue

        quantity = Decimal(str(quantity))
        pricing = product.get_pricing_for_quantity(quantity)
        discount_percent = int((pricing['discount_rate'] * 100).quantize(Decimal('1')))
        bag_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': pricing['subtotal'],
            'base_subtotal': pricing['base_total'],
            'discount_percent': discount_percent,
            'discounted_unit_price': (pricing['subtotal'] / quantity) if quantity else pricing['unit_price'],
            'savings': pricing['discount_amount'],
        })
        total += pricing['subtotal']
        product_count += quantity

    if total < free_delivery_threshold:
        delivery = total * (delivery_percentage / Decimal('100'))
        free_delivery_delta = free_delivery_threshold - total
    else:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')

    #grand_total = total + delivery

    return {
        'bag_items': bag_items,
        'bag_total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': total + delivery,
    }