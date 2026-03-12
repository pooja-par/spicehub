from .forms import NewsletterSignupForm


def newsletter_signup_form(request):
    return {"newsletter_form": NewsletterSignupForm()}