from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.featured_products, name='featured_products')
]