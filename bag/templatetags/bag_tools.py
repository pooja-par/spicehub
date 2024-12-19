from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter
def calc_subtotal(price, quantity):
    try:
        # Convert both price and quantity to Decimal
        price = Decimal(str(price))  # Ensure conversion to string before Decimal
        quantity = Decimal(str(quantity))  # Ensure conversion to string before Decimal
        return price * quantity
    except (InvalidOperation, ValueError, TypeError):
        # Return 0 if conversion fails
        return Decimal("0.00")
