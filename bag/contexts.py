 from decimal import Decimal
 from django.conf import settings
 from products.models import Product
 
 def bag_contents(request):
     """
     Context processor to make the shopping bag's contents globally available.
     """
     bag = request.session.get('bag', {})  # Retrieve the shopping bag session
     bag_items = []
     total = Decimal('0')  # Initialize total as Decimal
     product_count = 0
 
     # Fetch all products in a single query
     product_ids = bag.keys()
     products = Product.objects.filter(pk__in=product_ids)
     product_map = {str(product.id): product for product in products}
 
     for product_id, quantity in bag.items():
         product = product_map.get(str(product_id))  # Get product from the map
         if product:
             quantity = Decimal(str(quantity))  # Convert quantity to Decimal
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
 
     # Add delivery logic (if applicable)
     if total < settings.FREE_DELIVERY_THRESHOLD:
         delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)*2
         free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
     else:
         delivery = Decimal('0.00')
         free_delivery_delta = Decimal('0.00')
 
     grand_total = total + delivery
 
     # Return context
     context = {
         'bag_items': bag_items,
         'bag_total': total,  # Total price for all products
         'product_count': product_count,
         'delivery': delivery,
         'free_delivery_delta': free_delivery_delta,
         'grand_total': grand_total,
     }
     return context
