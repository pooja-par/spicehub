# products/management/commands/load_data.py
import json, os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from products.models import Category, Product

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
        if not force and (Category.objects.exists() or Product.objects.exists()):
            self.stdout.write("Initial data present; skipping fixtures.")
            return

        base = Path(settings.BASE_DIR)
        fx_dir = base / "products" / "fixtures"
        categories_fp = next((p for p in [fx_dir/"categories.json", base/"categories.json"] if p.exists()), None)
        products_fp   = next((p for p in [fx_dir/"products.json",   base/"products.json"]   if p.exists()), None)
        if not categories_fp or not products_fp:
            raise CommandError("categories.json/products.json not found. Put them in products/fixtures/.")

        def load_json(p: Path):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

        categories_data = load_json(categories_fp)
        products_data   = load_json(products_fp)

        def take_fields(item):
            # supports Django fixture style or plain dicts
            return item.get("fields", item)

        # Create categories
        for raw in categories_data:
            c = take_fields(raw)
            name = c["name"]
            slug = c.get("slug") or name.lower().replace(" ", "-")
            Category.objects.get_or_create(name=name, defaults={"slug": slug})

        cat_map = {c.name: c for c in Category.objects.all()}

        # Figure out product fields available on your model
        prod_fields = {f.name for f in Product._meta.get_fields()}
        price_field = "price_per_kg" if "price_per_kg" in prod_fields else ("price" if "price" in prod_fields else None)
        has_json_data = "json_data" in prod_fields
        has_image = "image" in prod_fields

        created = 0
        for raw in products_data:
            p = take_fields(raw)
            name = p["name"]
            slug = p.get("slug") or name.lower().replace(" ", "-")
            cat_name = p.get("category") or p.get("category_name")
            if not cat_name:
                raise CommandError(f"Product '{name}' missing 'category' field")
            category = cat_map.get(cat_name) or Category.objects.get(name=cat_name)

            defaults = {
                "slug": slug,
                "description": p.get("description", ""),
                "stock": p.get("stock", 0),
            }
            if price_field:
                defaults[price_field] = p.get(price_field) or p.get("price") or 0

            if has_image and "image" in p:
                # If you use Cloudinary, store a Cloudinary public_id or URL here
                defaults["image"] = p["image"]

            if has_json_data and "json_data" in p:
                defaults["json_data"] = p["json_data"]

            obj, was_created = Product.objects.get_or_create(
                name=name,
                category=category,
                defaults=defaults,
            )
            created += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Fixtures loaded. New products: {created}"))
