from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

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


class ProductCustomLogicTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='pepper', friendly_name='Pepper')

    def test_stock_status_thresholds(self):
        product = Product.objects.create(
            category=self.category,
            sku='SKU-10',
            name='Black Pepper',
            slug='black-pepper',
            description='Aromatic',
            price_per_kg='30.00',
            stock=3,
        )
        self.assertEqual(product.stock_status, 'critical_stock')

        product.stock = 20
        self.assertEqual(product.stock_status, 'low_stock')

        product.stock = 60
        self.assertEqual(product.stock_status, 'in_stock')

        product.stock = 0
        self.assertEqual(product.stock_status, 'out_of_stock')

    def test_get_pricing_for_quantity_applies_bulk_discount(self):
        product = Product.objects.create(
            category=self.category,
            sku='SKU-11',
            name='White Pepper',
            slug='white-pepper',
            description='Premium',
            price_per_kg='20.00',
            stock=120,
        )

        pricing = product.get_pricing_for_quantity('12')

        self.assertEqual(pricing['discount_percent'], 10)
        self.assertEqual(str(pricing['base_subtotal']), '240.00')
        self.assertEqual(str(pricing['subtotal']), '216.00')
        self.assertEqual(str(pricing['savings']), '24.00')


    def test_custom_discount_rules_override_default_tiers(self):
        product = Product.objects.create(
            category=self.category,
            sku='SKU-12',
            name='Chili Flakes',
            slug='chili-flakes',
            description='Hot',
            price_per_kg='10.00',
            stock=200,
            discount_rules=[
                {'minimum_quantity': 3, 'discount_rate': 0.08},
                {'minimum_quantity': 15, 'discount_rate': 0.2},
            ],
        )

        pricing = product.get_pricing_for_quantity('16')

        self.assertEqual(pricing['discount_percent'], 20)
        self.assertEqual(str(pricing['subtotal']), '128.00')

    def test_threshold_validation_rejects_invalid_configuration(self):
        product = Product(
            category=self.category,
            sku='SKU-13',
            name='Paprika',
            slug='paprika',
            description='Mild',
            price_per_kg='8.00',
            stock=50,
            low_stock_threshold=10,
            critical_stock_threshold=12,
        )

        with self.assertRaisesMessage(ValidationError, 'Critical threshold must be lower than low-stock threshold.'):
            product.full_clean()

    def test_invalid_discount_rules_are_rejected(self):
        product = Product(
            category=self.category,
            sku='SKU-14',
            name='Cumin',
            slug='cumin',
            description='Earthy',
            price_per_kg='9.00',
            stock=50,
            discount_rules=[{'minimum_quantity': 0, 'discount_rate': 1.2}],
        )

        with self.assertRaises(ValidationError):
            product.full_clean()