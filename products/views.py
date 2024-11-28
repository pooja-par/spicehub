from django.shortcuts import render, get_object_or_404
from .models import Product

def all_products(request):
    """
    A view to show all products, including sorting and search queries.
    """
    products = Product.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__name=category)

    if sort:
        if sort == 'price':
            products = products.order_by('price_per_kg')
        elif sort == 'rating':
            products = products.order_by('-rating')

    context = {
        'products': products,
        'search_term': query,
        'selected_category': category,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, slug):
    """
    A view to show individual product details by slug.
    """
    product = get_object_or_404(Product, slug=slug)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
