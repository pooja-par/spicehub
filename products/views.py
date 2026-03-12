from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.functions import Lower
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import get_object_or_404, redirect, render, reverse

from .forms import ProductForm
from .models import Category, Product


def _apply_product_filters(request, products):
    """Apply sorting, category, and search filters from query params."""
    query = None
    selected_categories = []
    sort = None
    direction = None

    if 'sort' in request.GET:
        sortkey = request.GET['sort']
        sort = sortkey

        if sortkey == 'name':
            products = products.annotate(lower_name=Lower('name'))
            sortkey = 'lower_name'
        elif sortkey == 'category':
            sortkey = 'category__name'

        direction = request.GET.get('direction')
        if direction == 'desc':
            sortkey = f'-{sortkey}'

        products = products.order_by(sortkey)

    if 'category' in request.GET and request.GET['category'].strip():
        selected_categories = [c for c in request.GET['category'].split(',') if c]
        products = products.filter(category__name__in=selected_categories)

    if 'q' in request.GET:
        query = request.GET['q'].strip()
        if not query:
            return products.none(), None, selected_categories, sort, direction, True

        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

    return products, query, selected_categories, sort, direction, False


def _build_related_products(product):
    """Return up to four in-stock products from the same category."""
    if not product.category:
        return []

    related_queryset = Product.objects.filter(category=product.category).exclude(pk=product.pk)
    related_products = [p for p in related_queryset if p.stock_status != 'out_of_stock']

    related_products.sort(
        key=lambda candidate: (
            abs(candidate.price_per_kg - product.price_per_kg),
            candidate.name.lower(),
        )
    )
    return related_products[:4]


def all_products(request):
    """Show all products, including sorting and search queries."""
    products = Product.objects.all()
    query = None
    selected_categories = []
    sort = None
    direction = None
    all_categories = []

    try:
        (
            products,
            query,
            selected_categories,
            sort,
            direction,
            invalid_search,
        ) = _apply_product_filters(request, products)

        if invalid_search:
            messages.error(request, "You didn't enter any search criteria!")
            return redirect(reverse('products'))

        all_categories = list(Category.objects.filter(is_active=True).order_by('friendly_name', 'name'))
        products = list(products)
    except (OperationalError, ProgrammingError):
        messages.warning(
            request,
            'Products are temporarily unavailable while the database is initializing. '
            'Please refresh in a moment.',
        )
        products = []
        all_categories = []
        query = None
        selected_categories = []
        sort = None
        direction = None

    context = {
        'products': products,
        'search_term': query,
        'categories': all_categories,
        'current_categories': selected_categories,
        'current_sorting': f'{sort}_{direction}',
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_slug):
    """Show an individual product detail page."""
    try:
        product = get_object_or_404(Product, slug=product_slug)
        related_products = _build_related_products(product)
    except (OperationalError, ProgrammingError):
        messages.warning(
            request,
            'Product details are temporarily unavailable while the database is initializing. '
            'Please refresh in a moment.',
        )
        return redirect(reverse('products'))

    return render(
        request,
        'products/product_detail.html',
        {'product': product, 'related_products': related_products},
    )


def _require_superuser(request):
    """Only superusers can access product management forms."""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can manage products.')
        raise PermissionDenied


@login_required
def add_product(request):
    """Add a product to the store."""
    _require_superuser(request)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save()
            except IntegrityError:
                messages.error(
                    request,
                    'A product with this slug already exists. Please choose a unique slug or rename the product.',
                )
            else:
                messages.success(request, f'Successfully added {product.name}.')
                return redirect(reverse('product_detail', args=[product.slug]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@login_required
def edit_product(request, product_slug):
    """Edit an existing product."""
    _require_superuser(request)

    product = get_object_or_404(Product, slug=product_slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                updated_product = form.save()
            except IntegrityError:
                messages.error(
                    request,
                    'A product with this slug already exists. Please choose a unique slug or rename the product.',
                )
            else:
                messages.success(request, f'Successfully updated {updated_product.name}.')
                return redirect(reverse('product_detail', args=[updated_product.slug]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}.')

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_slug):
    """Delete an existing product."""
    _require_superuser(request)

    product = get_object_or_404(Product, slug=product_slug)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Successfully deleted {product_name}.')
        return redirect(reverse('products'))

    return render(request, 'products/delete_product.html', {'product': product})