from decimal import Decimal

from django.conf import settings
from django.test import RequestFactory, TestCase, override_settings

from .contexts import bag_contents


class BagContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(FREE_DELIVERY_THRESHOLD=30, STANDARD_DELIVERY_PERCENTAGE=10)
    def test_bag_context_returns_empty_defaults_for_empty_session_bag(self):
        request = self.factory.get('/')
        request.session = {'bag': {}}

        context = bag_contents(request)

        self.assertEqual(context['bag_items'], [])
        self.assertEqual(context['bag_total'], Decimal('0.00'))
        self.assertEqual(context['free_delivery_delta'], Decimal('30'))

    def test_bag_context_uses_safe_fallback_when_delivery_settings_missing(self):
        request = self.factory.get('/')
        request.session = {'bag': {}}

        had_threshold = hasattr(settings, 'FREE_DELIVERY_THRESHOLD')
        had_percentage = hasattr(settings, 'STANDARD_DELIVERY_PERCENTAGE')
        original_threshold = getattr(settings, 'FREE_DELIVERY_THRESHOLD', None)
        original_percentage = getattr(settings, 'STANDARD_DELIVERY_PERCENTAGE', None)

        if had_threshold:
            delattr(settings, 'FREE_DELIVERY_THRESHOLD')
        if had_percentage:
            delattr(settings, 'STANDARD_DELIVERY_PERCENTAGE')

        try:
            context = bag_contents(request)
        finally:
            if had_threshold:
                setattr(settings, 'FREE_DELIVERY_THRESHOLD', original_threshold)
            if had_percentage:
                setattr(settings, 'STANDARD_DELIVERY_PERCENTAGE', original_percentage)

        self.assertEqual(context['delivery'], Decimal('0.00'))
        self.assertEqual(context['free_delivery_delta'], Decimal('30'))
        self.assertEqual(context['grand_total'], Decimal('0.00'))