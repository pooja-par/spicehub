from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):
    """
    Context processor to make the shopping bag's contents globally available.
    """
    bag = request.session.get('bag', {})  # Retrieve the shopping bag session
    bag_items = []
    total = Decimal('0')  # Initialize total as Decimal
    product_count = 0

    for product_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=product_id)
        quantity = Decimal(str(quantity))  # Convert quantity to Decimal
        subtotal = quantity * product.price_per_kg  # Consistent Decimal multiplication

        bag_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,  # Add subtotal
        })
        total += subtotal
        product_count += quantity

    # Return context
    context = {
        'bag_items': bag_items,
        'bag_total': total,  # Total price for all products
        'product_count': product_count,
        'grand_total': total,
    }
    return context
