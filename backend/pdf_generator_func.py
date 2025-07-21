from backend.models import ProductList 
from django.template.loader import render_to_string 
from django.http import HttpResponse 
from weasyprint import HTML  


def generate_pdf_from_template(request):

    product_id         = request.GET.get('product')
    casegory_id        = request.GET.get('category')
    sub_category_id    = request.GET.get('sub_category')
    child_category_id  = request.GET.get('child_category')
    created_from       = request.GET.get('created_from')
    created_to         = request.GET.get('created_to') 

    products = ProductList.objects.all()

    if product_id:
        products = products.filter(id=product_id)
    if casegory_id:
        products = products.filter(main_category_id=casegory_id)
    if sub_category_id:
        products = products.filter(sub_category_id=sub_category_id)
    if child_category_id:
        products = products.filter(child_category_id=child_category_id)
    if created_from:
        products = products.filter(created_at__date__gte=created_from)
    if created_to:
        products = products.filter(created_at__date__lte=created_to)

    products = products.filter(deleted=False)

    html_string         = render_to_string('product/pdf/pdf_template.html', {'products': products}) 
    base_url            = request.build_absolute_uri('/') if request else None 
    html                = HTML(string=html_string, base_url=base_url) 
    pdf                 = html.write_pdf()
    response            = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f"attachment; filename=output.pdf"

    return response 
                                                               


