from django.template.response import TemplateResponse
from django.shortcuts import render

# from backend.models import FrontendDesignSettings


# dynamic CSS
def dynamic_css(request):
    return TemplateResponse(request, "css/dynamic_styles.css", content_type="text/css")


# home
def home(request):
    
    return render(request, 'home/index.html')


# product_details
def product_show(request, slug):
    
    return render(request, 'products/product_show.html')


def homepage(request):
    return render(request, "homepage.html")
