from django.core.management.base import BaseCommand
from django.core.management import call_command, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
import os

class Command(BaseCommand):
    help = (
        "Idempotent startup tasks for production:\n"
        " - Ensure superuser from env vars\n"
        " - Load initial fixtures if DB is empty\n"
    )

    def handle(self, *args, **opts):
        self.ensure_superuser()
        self.ensure_initial_data()

    def ensure_superuser(self):
        """
        Create a superuser if not present, using env vars:
        DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
        Safe to run multiple times.
        """
        U = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write("Superuser envs not fully set; skipping superuser creation.")
            return

        if U.objects.filter(username=username).exists():
            self.stdout.write(f"Superuser '{username}' already exists; skipping.")
            return

        U.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f"Superuser '{username}' created.")

    @transaction.atomic
    def ensure_initial_data(self):
        """
        Load fixtures exactly once. If DB already has data, skip.
        You can force a reload by setting FORCE_LOAD_FIXTURES=1 (use with care).
        """
        from products.models import Product, Category  # import inside for app readiness

        force = os.getenv("FORCE_LOAD_FIXTURES") == "1"

        if not force:
            # Only load if both tables are empty (prevents duplicate key errors)
            if Category.objects.exists() or Product.objects.exists():
                self.stdout.write("Initial data present; skipping fixtures.")
                return

        fixtures = [
            "products/fixtures/categories.json",
            "products/fixtures/products.json",
        ]

        self.stdout.write("Loading initial fixtures…")
        for fx in fixtures:
            try:
                call_command("loaddata", fx, verbosity=0)
                self.stdout.write(f"  - loaded {fx}")
            except CommandError as e:
                self.stderr.write(f"  ! failed to load {fx}: {e}")
                raise
        self.stdout.write("Initial fixtures loaded.")
