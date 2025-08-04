from django.shortcuts import render
from .models import FeaturedProduct

def featured_products(request):
    featured = FeaturedProduct.objects.select_related('product')[:3]
    return {'featured_products': [fp.product for fp in featured]}
