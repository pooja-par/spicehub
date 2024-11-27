from django.shortcuts import render
#from .models import Product, Category, Order

# Create your views here.

def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')
