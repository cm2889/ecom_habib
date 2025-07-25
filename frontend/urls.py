from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/<str:slug>/', views.product_show, name='product_show'),

    path('theme.css', views.dynamic_css, name='theme_css'),
    path('', views.homepage, name='homepage'),
]
