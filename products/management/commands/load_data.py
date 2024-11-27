import json
from django.core.management.base import BaseCommand
from products.models import Category, Product

class Command(BaseCommand):
    help = 'Load bulk data into database'

    def handle(self, *args, **kwargs):
        with open('db.json', 'r') as file:
            data = json.load(file)

        for category_data in data['categories']:
            category, _ = Category.objects.get_or_create(
                name=category_data['name'],
                slug=category_data['slug']
            )

        for product_data in data['products']:
            category = Category.objects.get(name=product_data['category'])
            Product.objects.get_or_create(
                category=category,
                name=product_data['name'],
                slug=product_data['slug'],
                description=product_data['description'],
                price_per_kg=product_data['price_per_kg'],
                stock=product_data['stock'],
                image=product_data['image'],
                json_data=product_data['json_data']
            )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully!'))
