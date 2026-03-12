from django.shortcuts import render


def index(request):
    """Render the homepage."""
    return render(request, 'home/index.html')


def site_map(request):
    """Render the HTML sitemap page for users and crawlers."""
    return render(request, 'home/site_map.html')


def custom_404(request, exception):
    """Render the custom 404 page."""
    return render(request, '404.html', status=404)