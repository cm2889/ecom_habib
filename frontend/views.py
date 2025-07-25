from django.shortcuts import render

# Create your views here.

# home
def home(request):
    
    return render(request, 'home/index.html')

# product_details
def product_show(request, slug):
    
    return render(request, 'products/product_show.html')