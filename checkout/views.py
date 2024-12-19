from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "Your bag is empty")
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'ppk_test_51QXZBkAwymsVDFhSqmmLdUPfNO1I1EGYMye4Nzz1HJL9fbdfhjgwWxvuQBU7rZWO7f0sc8aKISBSzJw5Mmduao7N00ZZiRpim1',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)