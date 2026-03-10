from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.db.utils import OperationalError, ProgrammingError
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)
            
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    try:
        if request.GET:
            if 'sort' in request.GET:
                sortkey = request.GET['sort']
                sort = sortkey
                if sortkey == 'name':
                    sortkey = 'lower_name'
                    products = products.annotate(lower_name=Lower('name'))
                if sortkey == 'category':
                    sortkey = 'category__name'
                if 'direction' in request.GET:
                    direction = request.GET['direction']
                    if direction == 'desc':
                        sortkey = f'-{sortkey}'
                products = products.order_by(sortkey)

            if 'category' in request.GET:
                categories = request.GET['category'].split(',')
                products = products.filter(category__name__in=categories)
                categories = Category.objects.filter(name__in=categories)

            if 'q' in request.GET:
                query = request.GET['q']
                if not query:
                    messages.error(request, "You didn't enter any search criteria!")
                    return redirect(reverse('products'))

                queries = Q(name__icontains=query) | Q(description__icontains=query)
                products = products.filter(queries)

        # Force DB evaluation here so migration/table issues are caught and
        # handled instead of raising a 500 while rendering templates.
        products = list(products)
        if categories is not None:
            categories = list(categories)
    except (OperationalError, ProgrammingError):
        products = []
        categories = []
        messages.warning(
            request,
            'Products are temporarily unavailable while the database is initializing. '
            'Please refresh in a moment.',
        )

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_slug):
    """A view to show individual product details"""
    try:
        product = get_object_or_404(Product, slug=product_slug)
    except (OperationalError, ProgrammingError):
        messages.warning(
            request,
            'Product details are temporarily unavailable while the database is initializing. '
            'Please refresh in a moment.',
        )
        return redirect(reverse('products'))

    context = {'product': product}
    return render(request, 'products/product_detail.html', context)

def _require_superuser(request):
    """Only superusers can access product management forms."""
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can manage products.')
        return False
    return True


@login_required
def add_product(request):
    """ Add a product to the store """
    if not _require_superuser(request):
        return redirect(reverse('home'))

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
    if not _require_superuser(request):
        return redirect(reverse('home'))

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

    context = {
        'form': form,
        'product': product,
    }

    return render(request, 'products/edit_product.html', context)