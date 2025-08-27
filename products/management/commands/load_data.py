# products/management/commands/load_data.py
import json, os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Product

def field_names(model):
    return {f.name for f in model._meta.get_fields()}

class Command(BaseCommand):
    help = "Create superuser (from env) and load categories/products from fixtures. Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force reload even if data exists")

    def handle(self, *args, **opts):
        self.ensure_superuser()
        self.ensure_initial_data(force=opts["force"])

    def ensure_superuser(self):
        User = get_user_model()
        u = os.getenv("DJANGO_SUPERUSER_USERNAME")
        e = os.getenv("DJANGO_SUPERUSER_EMAIL")
        p = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not all([u, e, p]):
            self.stdout.write("Superuser envs not fully set; skipping superuser creation.")
            return
        if User.objects.filter(username=u).exists():
            self.stdout.write(f"Superuser '{u}' already exists; skipping.")
            return
        User.objects.create_superuser(username=u, email=e, password=p)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{u}' created."))

    @transaction.atomic
    def ensure_initial_data(self, force=False):
        # Skip if there is already data (unless --force)
        if not force and (Category.objects.exists() or Product.objects.exists()):
            self.stdout.write("Initial data present; skipping fixtures.")
            return

        base = Path(settings.BASE_DIR)
        fx_dir = base / "products" / "fixtures"
        categories_fp = next((p for p in [fx_dir/"categories.json", base/"categories.json"] if p.exists()), None)
        products_fp   = next((p for p in [fx_dir/"products.json",   base/"products.json"]   if p.exists()), None)
        if not categories_fp or not products_fp:
            raise CommandError("categories.json/products.json not found. Put them in products/fixtures/.")

        def load_json(path: Path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Support Django-fixture style OR plain list of dicts
            return [item.get("fields", item) for item in data]

        cats_data = load_json(categories_fp)
        prods_data = load_json(products_fp)

        cat_fields = field_names(Category)
        prod_fields = field_names(Product)

        # --- Categories ---
        for c in cats_data:
            name = c["name"]
            defaults = {}
            if "slug" in cat_fields and "slug" in c:
                defaults["slug"] = c["slug"]
            if "friendly_name" in cat_fields and "friendly_name" in c:
                defaults["friendly_name"] = c["friendly_name"]
            Category.objects.get_or_create(name=name, defaults=defaults)

        # Build lookups
        cats_by_name = {c.name: c for c in Category.objects.all()}
        cats_by_slug = {}
        if "slug" in cat_fields:
            cats_by_slug = {getattr(c, "slug", None): c for c in Category.objects.all() if getattr(c, "slug", None)}

        # Decide which price field your Product has
        price_field = "price_per_kg" if "price_per_kg" in prod_fields else ("price" if "price" in prod_fields else None)

        # --- Products ---
        for p in prods_data:
            name = p["name"]
            # Category may be referenced by name or slug in your JSON
            cat_key = p.get("category") or p.get("category_name") or p.get("category_slug")
            category = cats_by_name.get(cat_key) or cats_by_slug.get(cat_key)
            if not category:
                raise CommandError(f"Cannot find Category for product '{name}' using key '{cat_key}'")

            defaults = {}
            if "slug" in prod_fields:
                defaults["slug"] = p.get("slug") or name.lower().replace(" ", "-")
            if "description" in prod_fields:
                defaults["description"] = p.get("description", "")
            if "stock" in prod_fields:
                defaults["stock"] = p.get("stock", 0)
            if price_field:
                defaults[price_field] = p.get(price_field) or p.get("price") or 0
            if "image" in prod_fields and "image" in p:
                defaults["image"] = p["image"]  # Use a Cloudinary URL or public_id if you deploy with Cloudinary
            if "json_data" in prod_fields and "json_data" in p:
                defaults["json_data"] = p["json_data"]

            Product.objects.get_or_create(name=name, category=category, defaults=defaults)

        self.stdout.write(self.style.SUCCESS("Fixtures loaded successfully."))
