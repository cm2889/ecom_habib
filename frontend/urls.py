from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('theme.css', views.dynamic_css, name='theme_css'),

    path('', views.homepage, name='homepage'),
]
