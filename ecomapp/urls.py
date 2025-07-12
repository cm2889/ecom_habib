from django.urls import path
from . import views


urlpatterns = [
    path('', views.ecom_dashboard, name='dashboard'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('setting-dashboard/', views.setting_dashboard, name='setting_dashboard'),
    path('inventory-dashboard/', views.inventory_dashboard, name='inventory_dashboard'),
    path('cities/', views.cities, name='cities'),
    path('company-setting/', views.company_setting, name='company_setting'),
    path('add-new-company/', views.add_new_company, name='add_new_company'),

    # Products Information
    # Product main category URLs
    path('product-main-category-list/', views.product_main_category_list_view, name='product_main_category_list'),
    path('product-main-category-list/<int:pk>/', views.product_main_category_details_view, name='product_main_category_details_view'),
    path('add-product-main-category/', views.add_product_main_category, name='add_product_main_category'),
    path('product-main-category-update/<int:pk>/', views.product_main_category_update_view, name='product_main_category_update'),
    path('product-main-category-delete/<int:pk>/', views.product_main_category_delete_view, name='product_main_category_delete'),

    # Product sub category URLs
    path('product-sub-category-list/', views.product_sub_category_list_view, name='product_sub_category_list'),
    path('product-sub-category-detail/<int:pk>/', views.product_sub_category_details_view, name='product_sub_category_details_view'),
    path('add-product-sub-category/', views.product_sub_category_create_view, name='add_product_sub_category'),
    path('product-sub-category-update/<int:pk>/', views.product_sub_category_update_view, name='product_sub_category_update'),
    path('product-sub-category-delete/<int:pk>/', views.product_sub_category_delete_view, name='product_sub_category_delete'),

    # Product child category URLs
    path('product-child-category-list/', views.product_child_category_list_view, name='product_child_category_list'),
    path('product-child-category-detail/<int:pk>/', views.product_child_category_details_view, name='product_child_category_details_view'),
    path('add-product-child-category/', views.product_child_category_create_view, name='add_product_child_category'),
    path('product-child-category-update/<int:pk>/', views.product_child_category_update_view, name='product_child_category_update'),
    path('product-child-category-delete/<int:pk>/', views.product_child_category_delete_view, name='product_child_category_delete'),

    # Attribute list URLs
    # path('attribute-list/', views.attribute_list_view, name='attribute_list'),
    # path('add-attribute-list/', views.attribute_create_view, name='add_attribute_list'),
    # path('attribute-list-update/<int:pk>/', views.attribute_update_view, name='attribute_list_update'),
    # path('attribute-list-delete/<int:pk>/', views.attribute_delete_view, name='attribute_list_delete'),

    # Attribute value list URLs
    # path('attribute-value-list/', views.attribute_value_list_view, name='attribute_value_list'),
    # path('add-attribute-value-/', views.attribute_value_create_view, name='add_attribute_value_list'),
    # path('attribute-value-update/<int:pk>/', views.attribute_value_update_view, name='attribute_valuet_update'),
    # path('attribute-value-delete/<int:pk>/', views.attribute_value_delete_view, name='attribute_value_delete'),
]
