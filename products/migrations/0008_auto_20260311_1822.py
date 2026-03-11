from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_backfill_missing_product_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]