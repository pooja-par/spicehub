from django.test import TestCase
from django.urls import reverse

from .models import NewsletterSubscriber


class NewsletterSignupTests(TestCase):
    def test_signup_creates_subscriber(self):
        response = self.client.post(reverse("newsletter_signup"), {"email": "chef@example.com"})

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(NewsletterSubscriber.objects.filter(email="chef@example.com").exists())

    def test_duplicate_signup_does_not_create_multiple_records(self):
        NewsletterSubscriber.objects.create(email="repeat@example.com")

        self.client.post(reverse("newsletter_signup"), {"email": "repeat@example.com"})

        self.assertEqual(NewsletterSubscriber.objects.filter(email="repeat@example.com").count(), 1)

    def test_signup_normalizes_email_and_prevents_case_duplicate(self):
        NewsletterSubscriber.objects.create(email="repeat@example.com")

        self.client.post(reverse("newsletter_signup"), {"email": "Repeat@Example.com"})

        self.assertEqual(NewsletterSubscriber.objects.filter(email="repeat@example.com").count(), 1)