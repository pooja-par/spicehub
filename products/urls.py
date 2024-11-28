from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),  # All products page
    path('<slug:slug>/', views.product_detail, name='product_detail'),  # Product detail page
]
