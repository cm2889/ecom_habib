from django.urls import path
from . import views

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

    # # Product main category URLs
    path('product-main-category-list/', views.ProductMainCategoryListView.as_view(), name='product_main_category_list'),
    path('product-main-category-list/<int:pk>/', views.product_main_category_datails_view, name='product_main_category_details_view'),
    path('add-product-main-category/', views.ProductMainCategoryCreateView.as_view(), name='add_product_main_category'),
    path('product-main-category-update/<int:pk>/', views.ProductMainCategoryUpdateView.as_view(), name='product_main_category_update'),
    path('product-main-category-delete/<int:pk>/', views.product_main_category_delete_view, name='product_main_category_delete'),

    # Product sub category URLs
    path('product-sub-category-list/', views.ProductSubCategoryListView.as_view(), name='product_sub_category_list'),
    path('product-sub-category-detail/<int:pk>/', views.product_sub_category_details_view, name='product_sub_category_details_view'),
    path('add-product-sub-category/', views.ProductSubCategoryCreateView.as_view(), name='add_product_sub_category'),
    path('product-sub-category-update/<int:pk>/', views.ProductSubCategoryUpdateView.as_view(), name='product_sub_category_update'),
    path('product-sub-category-delete/<int:pk>/', views.product_sub_category_delete_view, name='product_sub_category_delete'),

    # # Product child category URLs
    path('product-child-category-list/', views.ProductChildCategoryListView.as_view(), name='product_child_category_list'),
    path('product-child-category-detail/<int:pk>/', views.product_child_category_details_view, name='product_child_category_details_view'),
    path('add-product-child-category/', views.ProductChildCategoryCreateView.as_view(), name='add_product_child_category'),
    path('product-child-category-update/<int:pk>/', views.ProductChildCategoryUpdateView.as_view(), name='product_child_category_update'),
    path('product-child-category-delete/<int:pk>/', views.product_child_category_delete_view, name='product_child_category_delete'),

    # Attribute list URLs
    path('attribute-list/', views.AttributeListView.as_view(), name='attribute_list'),
    path('attribute-details/<int:pk>/', views.attribute_details_view, name='attribute_details'),
    path('add-attribute-list/', views.AttributeCreateView.as_view(), name='add_attribute_list'),
    path('attribute-list-update/<int:pk>/', views.AttributeUpdateView.as_view(), name='attribute_list_update'),
    path('attribute-list-delete/<int:pk>/', views.attribute_delete_view, name='attribute_list_delete'),

    # Attribute value list URLs
    path('attribute-value-list/', views.AttributeValueListView.as_view(), name='attribute_value_list'),
    path('attribute-value-details/<int:pk>/', views.attribute_value_details_view, name='attribute_value_details'),
    path('add-attribute-value/', views.AttributeValueCreateView.as_view(), name='add_attribute_value_list'),
    path('attribute-value-update/<int:pk>/', views.AttributeValueUpdateView.as_view(), name='attribute_value_update'),
    path('attribute-value-delete/<int:pk>/', views.attribute_value_delete_view, name='attribute_value_delete'),

    # Product list URLs
    path('product-list/', views.ProductListView.as_view(), name='product_list'),
    path('product-details/<int:pk>/', views.product_details_view, name='product_details'),
    path('add-product/', views.ProductCreateView.as_view(), name='add_product'),
    path('product-update/<int:pk>/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product-delete/<int:pk>/', views.product_delete_view, name='product_delete'),


    # Product attribute URLs
    path('product-attribute-list/', views.ProductAttibuteListView.as_view(), name='product_attribute_list'),
    path('product-attribute-details/<int:pk>/', views.product_attribute_details_view, name='product_attribute_details'),
    path('add-product-attribute/', views.ProductAttributeCreateView.as_view(), name='add_product_attribute'),
    path('product-attribute-update/<int:pk>/', views.ProductAttributeUpdateView.as_view(), name='product_attribute_update'),
    path('product-attribute-delete/<int:pk>/', views.product_attribute_delete_view, name='product_attribute_delete'),
]
