from django import forms

from .models import NewsletterSubscriber


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]

    def clean_email(self):
        """Store emails normalized to lowercase to avoid duplicate variants."""
        email = self.cleaned_data["email"].strip().lower()
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your email",
                "aria-label": "Email address",
            }
        )