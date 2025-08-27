# products/management/commands/load_data.py
import json, os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Product

def model_fields(model):
    return {f.name for f in model._meta.get_fields()}

def normalize_list(data, top_key=None):
    """
    Accepts:
    - a plain list of objects
    - a Django-style fixture list [ {"model": "...", "pk": ..., "fields": {...}}, ... ]
    - a dict with a top-level key (e.g. {"categories": [...]}) if top_key is provided
    Returns list of dicts: {"_pk": pk or None, **fields}
    """
    if isinstance(data, dict) and top_key and top_key in data:
        data = data[top_key]
    if not isinstance(data, list):
        raise CommandError("Fixture must be a list or a dict containing a list under the expected key.")
    out = []
    for item in data:
        if isinstance(item, dict) and "fields" in item:
            fields = dict(item["fields"])
            pk = item.get("pk") or item.get("id")
        else:
            fields = dict(item)
            pk = item.get("id") or item.get("pk")
        fields["_pk"] = pk
        out.append(fields)
    return out

class Command(BaseCommand):
    help = "Create superuser (from env) and load categories/products (idempotent). Supports name, slug, or numeric category references."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Force re-load (still idempotent)")

    def handle(self, *args, **opts):
        self.ensure_superuser()
        self.load_categories_and_products(force=opts["force"])

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
    def load_categories_and_products(self, force=False):
        base = Path(settings.BASE_DIR)
        fx_dir = base / "products" / "fixtures"

        categories_fp = next((p for p in [fx_dir/"categories.json", base/"categories.json"] if p.exists()), None)
        products_fp   = next((p for p in [fx_dir/"products.json",   base/"products.json"]   if p.exists()), None)
        if not categories_fp or not products_fp:
            raise CommandError("categories.json/products.json not found. Put them under products/fixtures/.")

        # Load raw JSON
        with open(categories_fp, "r", encoding="utf-8") as f:
            cats_raw = json.load(f)
        with open(products_fp, "r", encoding="utf-8") as f:
            prods_raw = json.load(f)

        cats_list  = normalize_list(cats_raw,  top_key="categories")
        prods_list = normalize_list(prods_raw, top_key="products")

        cat_fields = model_fields(Category)
        prod_fields = model_fields(Product)

        # Create/update categories idempotently; remember JSON pk -> Category
        pk_to_category = {}
        name_to_category = {}
        slug_to_category = {}

        for c in cats_list:
            name = c["name"]
            defaults = {}
            if "slug" in cat_fields and "slug" in c:
                defaults["slug"] = c["slug"]
            if "friendly_name" in cat_fields and "friendly_name" in c:
                defaults["friendly_name"] = c["friendly_name"]

            cat_obj, _ = Category.objects.get_or_create(name=name, defaults=defaults)
            pk = c.get("_pk")
            if pk is not None:
                try:
                    pk_to_category[int(pk)] = cat_obj
                except Exception:
                    pass  # ignore non-int pk

            name_to_category[name] = cat_obj
            if "slug" in cat_fields and getattr(cat_obj, "slug", None):
                slug_to_category[getattr(cat_obj, "slug")] = cat_obj

        # Decide product price field
        price_field = "price_per_kg" if "price_per_kg" in prod_fields else ("price" if "price" in prod_fields else None)

        created = 0
        for p in prods_list:
            name = p["name"]

            # Resolve category reference: numeric pk OR name OR slug
            cat_key = p.get("category") or p.get("category_name") or p.get("category_slug")
            category = None
            if isinstance(cat_key, int) or (isinstance(cat_key, str) and cat_key.isdigit()):
                category = pk_to_category.get(int(cat_key))
            if not category and isinstance(cat_key, str):
                category = name_to_category.get(cat_key) or slug_to_category.get(cat_key)
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
                # Best: use a Cloudinary URL or public_id here for Render/Heroku
                defaults["image"] = p["image"]
            if "json_data" in prod_fields and "json_data" in p:
                defaults["json_data"] = p["json_data"]

            obj, was_created = Product.objects.get_or_create(
                name=name,
                category=category,
                defaults=defaults,
            )
            created += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Loaded fixtures. New products created: {created}"))
