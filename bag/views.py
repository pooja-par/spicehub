from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from products.models import Product

# View to render the bag contents page
def view_bag(request):
    """ A view that renders the bag contents page """
    return render(request, 'bag/bag.html')

# View to add a product to the shopping bag
def add_to_bag(request, product_id):
    """
    Add a specified quantity of the product in kilograms to the shopping bag.
    """
    product = get_object_or_404(Product, pk=product_id)
    redirect_url = request.POST.get('redirect_url', '/products/')
    
    # Handle quantity safely
    try:
        quantity = float(request.POST.get('quantity', 0))
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
    except ValueError:
        messages.error(request, "Please enter a valid quantity.")
        return redirect(redirect_url)

    # Fetch or initialize the session bag
    bag = request.session.get('bag', {})

    # Add or update product quantity in the bag
    if str(product_id) in bag:
        bag[str(product_id)] += quantity
        messages.success(request, f'Updated {product.name} quantity to {bag[str(product_id)]} kg.')
    else:
        bag[str(product_id)] = quantity
        messages.success(request, f'Added {product.name} to your bag.')


    request.session['bag'] = bag
    return redirect(redirect_url)

# View to remove a product from the shopping bag
def remove_from_bag(request, product_id):
    """
    Remove a product from the shopping bag.
    """
    product = get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {})
    
    if str(product_id) in bag:
        del bag[str(product_id)]
        messages.success(request, f'{product.name} is removed from your bag')
    else:
        messages.success(request, f'{product.name} is not found in your bag')

    request.session['bag'] = bag
    return redirect('view_bag')

# View to display the checkout page
def checkout(request):
    """
    A view to display the checkout page.
    """
    return render(request, 'checkout/checkout.html')


