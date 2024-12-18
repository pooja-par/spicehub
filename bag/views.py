from django.shortcuts import render, redirect

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')


def add_to_bag(request, product_id):
    """
    Add a specified quantity of the product in kilograms to the shopping bag.
    """
    quantity = float(request.POST.get('quantity'))  # Allow decimal input for kg
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    if product_id in bag:
        bag[product_id] += quantity
    else:
        bag[product_id] = quantity

    request.session['bag'] = bag
    return redirect(redirect_url)



def remove_from_bag(request, product_id):
    """
    Remove a product from the shopping bag.
    """
    bag = request.session.get('bag', {})  # Fetch current bag
    #product = get_object_or_404(Product, pk=product_id)

    if str(product_id) in bag:
        del bag[str(product_id)]  # Remove the product from the bag
        request.session['bag'] = bag  # Save updated bag in session

    return redirect('view_bag')  # Redirect to the bag page


def checkout(request):
    """
    A view to display the checkout page.
    """
    return render(request, 'checkout/checkout.html')