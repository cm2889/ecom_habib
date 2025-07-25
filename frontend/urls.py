from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/<str:slug>/', views.product_show, name='product_show'),
]
