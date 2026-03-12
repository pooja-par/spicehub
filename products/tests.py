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

    def test_add_product_with_duplicate_name_generates_unique_slug(self):
        self.client.login(username='owner', password='testpass123')

        Product.objects.create(
            category=self.category,
            sku='SKU-EXIST',
            name='Onion Powder',
            slug='onion-powder',
            description='Existing',
            price_per_kg='9.00',
            stock=5,
        )

        response = self.client.post(reverse('add_product'), data={
            'category': self.category.id,
            'sku': 'SKU-NEW',
            'name': 'Onion Powder',
            'slug': '',
            'description': 'Second row',
            'price_per_kg': '10.00',
            'stock': 8,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Onion Powder', slug='onion-powder-2').exists())

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
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Garlic Flakes Premium')
        self.assertEqual(str(self.product.price_per_kg), '24.00')

    def test_anonymous_user_is_redirected_to_login_for_product_management_views(self):
        add_response = self.client.get(reverse('add_product'))
        edit_response = self.client.get(reverse('edit_product', args=[self.product.slug]))
        delete_response = self.client.get(reverse('delete_product', args=[self.product.slug]))

        self.assertEqual(add_response.status_code, 302)
        self.assertIn(reverse('account_login'), add_response.url)
        self.assertEqual(edit_response.status_code, 302)
        self.assertIn(reverse('account_login'), edit_response.url)
        self.assertEqual(delete_response.status_code, 302)
        self.assertIn(reverse('account_login'), delete_response.url)

    def test_regular_user_gets_forbidden_for_product_management_views(self):
        self.client.login(username='shopper', password='testpass123')

        add_response = self.client.get(reverse('add_product'))
        edit_response = self.client.get(reverse('edit_product', args=[self.product.slug]))
        delete_response = self.client.get(reverse('delete_product', args=[self.product.slug]))

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)

    def test_regular_user_cannot_post_to_product_management_views(self):
        self.client.login(username='shopper', password='testpass123')

        add_response = self.client.post(reverse('add_product'), data={
            'category': self.category.id,
            'sku': 'SKU-LOCKED',
            'name': 'Blocked Product',
            'slug': '',
            'description': 'Should never be created',
            'price_per_kg': '10.00',
            'stock': 3,
        })
        edit_response = self.client.post(
            reverse('edit_product', args=[self.product.slug]),
            data={
                'category': self.category.id,
                'sku': self.product.sku,
                'name': 'Unauthorized Update',
                'slug': self.product.slug,
                'description': self.product.description,
                'price_per_kg': '22.00',
                'stock': self.product.stock,
            },
        )
        delete_response = self.client.post(reverse('delete_product', args=[self.product.slug]))

        self.assertEqual(add_response.status_code, 403)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertFalse(Product.objects.filter(name='Blocked Product').exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Garlic Flakes')
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class ProductCustomLogicTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='spice', friendly_name='Spice')

    def test_critical_threshold_must_be_lower_than_low_stock_threshold(self):
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
    def test_model_save_generates_unique_slug_when_missing(self):
        first = Product.objects.create(
            category=self.category,
            sku='SKU-15',
            name='Smoked Paprika',
            slug='',
            description='Smoky',
            price_per_kg='11.00',
            stock=10,
        )
        second = Product.objects.create(
            category=self.category,
            sku='SKU-16',
            name='Smoked Paprika',
            slug='',
            description='Smoky second',
            price_per_kg='12.00',
            stock=10,
        )

        self.assertEqual(first.slug, 'smoked-paprika')
        self.assertEqual(second.slug, 'smoked-paprika-2')


class ProductAdminTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username='adminowner', email='adminowner@example.com', password='testpass123'
        )
        self.category = Category.objects.create(name='paprika', friendly_name='Paprika')

    def test_admin_add_product_works_with_image_value(self):
        self.client.login(username='adminowner', password='testpass123')

        response = self.client.post('/admin/products/product/add/', data={
            'category': self.category.id,
            'sku': 'SKU-ADMIN-1',
            'name': 'Admin Added Product',
            'slug': '',
            'description': 'Added through admin form',
            'price_per_kg': '15.00',
            'stock': 12,
            'image': 'spices/admin-added.jpg',
            'low_stock_threshold': 25,
            'critical_stock_threshold': 5,
            'discount_rules': '[]',
            '_save': 'Save',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Admin Added Product').exists())


class ProductPublicViewsTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='spices', friendly_name='Spices')

    def test_products_page_renders_when_legacy_product_slug_is_blank(self):
        Product.objects.create(
            category=self.category,
            sku='SKU-17',
            name='Legacy Cinnamon',
            slug='',
            description='Legacy row with empty slug',
            price_per_kg='13.00',
            stock=6,
        )

        response = self.client.get(reverse('products'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Legacy Cinnamon')