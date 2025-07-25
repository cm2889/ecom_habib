from django.http import HttpResponse
from openpyxl import Workbook
from backend.models import ProductList


def export_products_to_excel(request):
    product_id = request.GET.get('product')
    category_id = request.GET.get('category')
    sub_category_id = request.GET.get('sub_category')
    child_category_id = request.GET.get('child_category')
    created_from = request.GET.get('created_from')
    created_to = request.GET.get('created_to')

    products = ProductList.objects.all()

    if product_id:
        products = products.filter(id=product_id)
    if category_id:
        products = products.filter(main_category_id=category_id)
    if sub_category_id:
        products = products.filter(sub_category_id=sub_category_id)
    if child_category_id:
        products = products.filter(child_category_id=child_category_id)
    if created_from:
        products = products.filter(created_at__date__gte=created_from)
    if created_to:
        products = products.filter(created_at__date__lte=created_to)
    products = products.filter(deleted=False)

    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    headers = [
        'Name', 'SKU', 'Slug', 'Brand', 'Category', 'Sub Category', 'Child Category', 'Unit Price',
        'Sale Price', 'Stock Status', 'Available Qty', 'Created At', 'Status'
    ]
    ws.append(headers)

    for product in products:
        try:
            ws.append([
                product.product_name,
                product.product_sku,
                product.product_slug,
                product.brand.name if product.brand and product.brand.name else '',
                product.main_category.name if product.main_category and product.main_category.name else '',
                product.sub_category.name if product.sub_category and product.sub_category.name else '',
                product.child_category.name if product.child_category and product.child_category.name else '',
                product.unit_price,
                product.sale_price,
                product.stock_status,
                product.available_qty,
                product.created_at.strftime("%Y-%m-%d") if product.created_at else '',
                "Active" if product.is_active else "Inactive"
            ])
        except Exception as e:
            print(f"Error processing product {product.id}: {e}")

    # Prepare HTTP response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = "Products List.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)

    return response
