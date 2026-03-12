from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from checkout.models import Order

from .forms import UserProfileForm
from .models import UserProfile


@login_required
def profile(request):
    """Display and update the authenticated user's profile."""
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
        else:
            messages.error(request, 'Update failed. Please check the form and try again.')
    else:
        form = UserProfileForm(instance=user_profile)

    orders = user_profile.orders.all()

    return render(
        request,
        'profiles/profile.html',
        {
            'form': form,
            'orders': orders,
            'on_profile_page': True,
        },
    )


@login_required
def order_history(request, order_number):
    """Show a past order confirmation that belongs to the logged-in user."""
    user_profile = get_object_or_404(UserProfile, user=request.user)
    order = get_object_or_404(Order, order_number=order_number, user_profile=user_profile)

    messages.info(
        request,
        (
            f'This is a past confirmation for order number {order_number}. '
            'A confirmation email was sent on the order date.'
        ),
    )

    return render(
        request,
        'checkout/checkout_success.html',
        {
            'order': order,
            'from_profile': True,
        },
    )