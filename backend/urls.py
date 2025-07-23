from django.urls import path
from . import views
from . import export_function
from . import pdf_generator_func 

app_name = 'backend' 

urlpatterns = [
    path('', views.backend_dashboard, name='backend_dashboard'),
    path('login/', views.backend_login, name='backend_login'),
    path('logout/', views.backend_logout, name='backend_logout'),

    # User Mannagement
    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/add/', views.user_add, name='user_add'),
    path('user/update/<str:data_id>/', views.user_update, name='user_update'),
    path('user/password/reset/<str:data_id>/', views.reset_password, name='reset_password'),
    path('user/permission/<int:user_id>/', views.user_permission, name='user_permission'),

    # Inventory Management
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),

    # Setting
    path('settings/', views.setting_dashboard, name='setting_dashboard'),
    path('website-setting/', views.website_setting, name='website_setting'),
    path('email-configuration/', views.EmailConfigurationCreateUpdateView.as_view(), name='email_configuration'),
    path('sms-configuration/', views.SMSConfigurationCreateUpdateView.as_view(), name='sms_configuration'),

    # path('cities/', views.cities, name='cities'),
    # path('company-setting/', views.company_setting, name='company_setting'),
    # path('add-new-company/', views.add_new_company, name='add_new_company'),

    # Product brand
    path('brand/', views.BrandListView.as_view(), name='brand_list'),
    path('brand-details/<int:pk>/', views.brand_detail_view, name='brand_details_view'),
    path('add-brand/', views.BrandCreateView.as_view(), name='add_brand'),
    path('brand-update/<int:pk>/', views.BrandUpdateView.as_view(), name='brand_update'),
    path('brand-delete/<int:pk>/', views.brand_delete_view, name='brand_delete'),


    # Product main category URLs
    path('category/', views.MainCategoryListView.as_view(), name='category_list'),
    path('category-details/<int:pk>/', views.category_detail_view, name='category_detail_view'),
    path('add-category/', views.CategoryCreateView.as_view(), name='add_category'),
    path('category-update/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category-delete/<int:pk>/', views.category_delete_view, name='product_main_category_delete'),
    path('upload-category-excel/', views.upload_category_excel, name='upload_category_excel'), 

    # Product sub category URLs
    path('sub-category/', views.SubCategoryListView.as_view(), name='sub_category_list'),
    path('sub-category-detail/<int:pk>/', views.sub_category_details_view, name='sub_category_details_view'),
    path('add-sub-category/', views.SubCategoryCreateView.as_view(), name='add_sub_category'),
    path('sub-category-update/<int:pk>/', views.SubCategoryUpdateView.as_view(), name='sub_category_update'),
    path('sub-category-delete/<int:pk>/', views.sub_category_delete_view, name='sub_category_delete'),
    path('upload-sub-category-excel/', views.upload_sub_category_excel, name='upload_sub_category_excel'),

    # # Product child category URLs
    path('child-category/', views.ChildCategoryListView.as_view(), name='child_category_list'),
    path('child-category-detail/<int:pk>/', views.child_category_details_view, name='child_category_details_view'),
    path('add-child-category/', views.ChildCategoryCreateView.as_view(), name='add_child_category'),
    path('child-category-update/<int:pk>/', views.ChildCategoryUpdateView.as_view(), name='child_category_update'),
    path('child-category-delete/<int:pk>/', views.child_category_delete_view, name='child_category_delete'),
    path('upload-child-category-excel/', views.upload_child_category_excel, name='upload_child_category_excel'), 

    # Attribute list URLs
    path('attributes/', views.AttributeListView.as_view(), name='attribute_list'),
    path('attribute-details/<int:pk>/', views.attribute_details_view, name='attribute_details'),
    path('add-attribute/', views.AttributeCreateView.as_view(), name='add_attribute_list'),
    path('attribute-list-update/<int:pk>/', views.AttributeUpdateView.as_view(), name='attribute_list_update'),
    path('attribute-list-delete/<int:pk>/', views.attribute_delete_view, name='attribute_list_delete'),

    # Attribute value list URLs
    path('attribute-value-list/', views.AttributeValueListView.as_view(), name='value_list'),
    path('attribute-value-details/<int:pk>/', views.value_details_view, name='value_details'),
    path('add-attribute-value/', views.AttributeValueCreateView.as_view(), name='add_value_list'),
    path('attribute-value-update/<int:pk>/', views.AttributeValueUpdateView.as_view(), name='value_update'),
    path('attribute-value-delete/<int:pk>/', views.value_delete_view, name='value_delete'),

    # Product list URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product-details/<int:pk>/', views.product_details_view, name='product_details'),
    path('add-product/', views.ProductCreateView.as_view(), name='add_product'),
    path('product-update/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product-delete/<int:pk>/', views.product_delete_view, name='product_delete'),
    path('download-product-excel/', export_function.export_products_to_excel, name='export_products_to_excel'),
    path('upload-product-excel/', views.upload_product_excel, name='upload_product_excel'),
    path('download-product-pdf/', pdf_generator_func.generate_pdf_from_template, name='export_products_to_pdf'), 

    # Product attribute URLs
    path('product-attribute-list/', views.ProductAttibuteListView.as_view(), name='product_attribute_list'),
    path('product-attribute-details/<int:pk>/', views.product_attribute_details_view, name='product_attribute_details'),
    path('add-product-attribute/', views.ProductAttributeCreateView.as_view(), name='add_product_attribute'),
    path('product-attribute-update/<int:pk>/', views.ProductAttributeUpdateView.as_view(), name='product_attribute_update'),
    path('product-attribute-delete/<int:pk>/', views.product_attribute_delete_view, name='product_attribute_delete'),
]
