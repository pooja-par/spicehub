from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from .forms import NewsletterSignupForm
from .models import NewsletterSubscriber


@require_POST
def signup(request):
    form = NewsletterSignupForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data["email"]
        _, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            messages.success(request, "Thanks for subscribing to our newsletter!")
        else:
            messages.info(request, "You're already subscribed to our newsletter.")
    else:
        messages.error(request, "Please enter a valid email address.")

    return redirect(request.POST.get("next") or request.META.get("HTTP_REFERER") or "home")