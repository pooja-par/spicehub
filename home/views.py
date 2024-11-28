from django.shortcuts import render, redirect
#from .models import CartItem
from products.models import Product

# Create your views here.

def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')

'''
def cart_view(request):
    session_id = request.session.session_key or request.session.create()
    cart_items = CartItem.objects.filter(session_id=session_id)
    total = sum(item.subtotal() for item in cart_items)

    return render(request, 'home/cart.html', {'cart_items': cart_items, 'total': total})


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    session_id = request.session.session_key or request.session.create()

    cart_item, created = CartItem.objects.get_or_create(
        product=product,
        session_id=session_id,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')
'''