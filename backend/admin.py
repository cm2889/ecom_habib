from django.contrib import admin

from .models import (
    LoginLog, BackendMenu, UserMenuPermission, ProductMainCategory,
    ProductSubCategory, ProductChildCategory, AttributeList, AttributeValueList, ProductList, ProductAttribute
)


@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'wrong_password', 'login_ip', 'login_status', 'created_at')
    list_filter = ('login_status',)


# @admin.register(UserGroup)
# class UserGroupAdmin(admin.ModelAdmin):
#     list_display = ('group_name', 'description', 'created_by', 'created_at', 'updated_at', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('group_name', 'description')
#     ordering = ('created_at',)


# @admin.register(GroupWiseMenu)
# class GroupWiseMenuAdmin(admin.ModelAdmin):
#     list_display = ('user_group', 'menu', 'can_view', 'can_add', 'can_update', 'can_delete', 'created_at', 'updated_at', 'is_active')
#     list_filter = ('is_active',)
#     ordering = ('created_at',)


# @admin.register(BackendMenu)
# class BackendMenuAdmin(admin.ModelAdmin):
#     list_display = ('module_name', 'menu_name', 'menu_url', 'menu_icon', 'parent_id', 'created_by', 'created_at', 'updated_at', 'is_active')
#     list_filter = ('is_active', 'is_main_menu', 'is_sub_menu')
#     search_fields = ('module_name', 'menu_name', 'menu_url')
#     ordering = ('parent_id', 'menu_name')


# @admin.register(EmployeeType)
# class EmployeeTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'created_at', 'updated_at', 'is_active', 'deleted')
#     list_filter = ('is_active', 'deleted')
#     search_fields = ('name', 'description')
#     ordering = ('created_at',)


# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = ('employee_id_number', 'user', 'date_of_birth', 'gender', 'created_at', 'updated_at', 'is_active', 'deleted')
#     list_filter = ('is_active', 'deleted')
#     search_fields = ('fathers_name', 'mothers_name', 'user__username', 'email')
#     ordering = ('created_at',)



# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name', 'state', 'country', 'created_at', 'updated_at', 'is_active', 'deleted')
#     list_filter = ('is_active', 'deleted')
#     ordering = ('created_at',)


# @admin.register(Company)
# class CompanyAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'website', 'phone', 'industry', 'address', 'created_at', 'updated_at', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'email', 'industry')
#     ordering = ('created_at',)


@admin.register(UserMenuPermission)
class UserMenuPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu', 'can_view',  'can_add', 'can_update', 'can_delete', 'created_at', 'updated_at', 'is_active', 'deleted')
    list_filter = ('is_active', 'deleted')
    ordering = ('created_at',)



@admin.register(ProductMainCategory)
class ProductMainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('ordering',)


@admin.register(ProductSubCategory)
class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('ordering',)


@admin.register(ProductChildCategory)
class ProductChildCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    ordering = ('ordering',)


@admin.register(AttributeList)
class AttributeListAdmin(admin.ModelAdmin):
    list_display = ('name', 'ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('ordering',)


@admin.register(AttributeValueList)
class AttributeValueListAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'ordering', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('attribute__name', 'value')
    ordering = ('ordering',)


@admin.register(ProductList)
class ProductListAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_sku', 'main_category', 'unit_price', 'sale_price', 'discount_percent', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product_name', 'product_slug')
    ordering = ('product_ordering',)


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value', 'created_by', 'updated_by', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active',)
    ordering = ('created_at',)
