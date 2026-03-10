from django.db import migrations
from django.utils.text import slugify


def backfill_missing_product_slugs(apps, schema_editor):
    Product = apps.get_model('products', 'Product')

    for product in Product.objects.filter(slug='').order_by('id'):
        base_slug = slugify(product.name or '') or f'product-{product.id}'
        slug_candidate = base_slug
        suffix = 2

        while Product.objects.exclude(pk=product.pk).filter(slug=slug_candidate).exists():
            slug_candidate = f'{base_slug}-{suffix}'
            suffix += 1

        product.slug = slug_candidate
        product.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_auto_20260309_0955'),
    ]

    operations = [
        migrations.RunPython(backfill_missing_product_slugs, migrations.RunPython.noop),
    ]