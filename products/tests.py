from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from .forms import ProductForm
from .models import Category, Product


class ProductFormTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='onion', friendly_name='Onion')

    def test_price_per_kg_must_be_positive(self):
        form = ProductForm(data={
            'category': self.category.id,
            'sku': 'SKU-1',
            'name': 'Bad Product',
            'description': 'Invalid price',
            'price_per_kg': '0',
            'stock': 4,
        })

        self.assertFalse(form.is_valid())
        self.assertIn('price_per_kg', form.errors)

    def test_slug_is_generated_from_name_when_missing(self):
        form = ProductForm(data={
            'category': self.category.id,
            'sku': 'SKU-2',
            'name': 'Fresh Garlic Powder',
            'description': 'Good',
            'price_per_kg': '12.50',
            'stock': 5,
            'slug': '',
        })

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['slug'], 'fresh-garlic-powder')


class ProductManagementViewsTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username='owner', email='owner@example.com', password='testpass123'
        )
        self.regular_user = user_model.objects.create_user(
            username='shopper', email='shopper@example.com', password='testpass123'
        )
        self.category = Category.objects.create(name='garlic', friendly_name='Garlic')
        self.product = Product.objects.create(
            category=self.category,
            sku='SKU-3',
            name='Garlic Flakes',
            slug='garlic-flakes',
            description='Great flakes',
            price_per_kg='20.00',
            stock=10,
        )

    def test_add_product_creates_product_for_superuser(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.post(reverse('add_product'), data={
            'category': self.category.id,
            'sku': 'SKU-4',
            'name': 'Onion Powder',
            'slug': '',
            'description': 'Fine texture',
            'price_per_kg': '10.00',
            'stock': 8,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Onion Powder', slug='onion-powder').exists())

    def test_edit_product_updates_existing_product_for_superuser(self):
        self.client.login(username='owner', password='testpass123')

        response = self.client.post(
            reverse('edit_product', args=[self.product.slug]),
            data={
                'category': self.category.id,
                'sku': self.product.sku,
                'name': 'Garlic Flakes Premium',
                'slug': 'garlic-flakes-premium',
                'description': self.product.description,
                'price_per_kg': '24.00',
                'stock': self.product.stock,
            }
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Garlic Flakes Premium')
        self.assertEqual(str(self.product.price_per_kg), '24.00')

    def test_regular_user_cannot_access_add_or_edit_product_forms(self):
        self.client.login(username='shopper', password='testpass123')

        add_response = self.client.get(reverse('add_product'))
        edit_response = self.client.get(reverse('edit_product', args=[self.product.slug]))

        self.assertEqual(add_response.status_code, 302)
        self.assertEqual(edit_response.status_code, 302)
        self.assertFalse(Product.objects.filter(name='Unauthorized Product').exists())