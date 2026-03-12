from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import Product


class StaticViewSitemap(Sitemap):
    """Sitemap entries for public static routes."""

    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'products', 'contact']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Sitemap entries for in-stock products."""

    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Product.objects.filter(stock__gt=0).order_by('id')

    def lastmod(self, obj):
        return None

    def location(self, obj):
        return reverse('product_detail', kwargs={'product_slug': obj.slug})