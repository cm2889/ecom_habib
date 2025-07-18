from django.apps import apps
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, AdminPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages

from datetime import datetime

from backend.common_func import checkUserPermission
from backend.decorators import admin_required
from backend.models import (
    LoginLog, AdminUser, BackendMenu, UserMenuPermission
)
from backend.forms import (
    CustomUserLoginForm, UserCreateForm
)


# from .models import ProductMainCategory, ProductSubCategory, ProductChildCategory, AttributeList, AttributeValueList 

# from .forms import ProductMainCategoryForm, ProductSubCategoryForm, ProductChildCategoryForm, AttributeListForm, AttributeValueListForm


def paginate_data(request, page_num, data_list):
    items_per_page, max_pages = 10, 10
    paginator = Paginator(data_list, items_per_page)
    last_page_number = paginator.num_pages

    try:
        data_list = paginator.page(page_num)
    except PageNotAnInteger:
        data_list = paginator.page(1)
    except EmptyPage:
        data_list = paginator.page(paginator.num_pages)

    current_page = data_list.number
    start_page = max(current_page - int(max_pages / 2), 1)
    end_page = start_page + max_pages

    if end_page > last_page_number:
        end_page = last_page_number + 1
        start_page = max(end_page - max_pages, 1)

    paginator_list = range(start_page, end_page)

    return data_list, paginator_list, last_page_number


@admin_required
def backend_dashboard(request):
    return render(request, 'home/home.html')


def backend_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = CustomUserLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user_ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

        user = User.objects.filter(username=username).first()

        if user and (user.is_superuser or hasattr(user, 'admin')):
            authenticated_user = authenticate(request, username=username, password=password)

            if authenticated_user is not None:
                if user.is_superuser and not hasattr(user, 'admin'):
                    AdminUser.objects.create(user=user)

                login(request, authenticated_user)
                LoginLog.objects.create(user_id=user.id, username=username, login_ip=user_ip, login_status=True)

                next_url = request.GET.get('next', reverse('backend_dashboard'))
                return redirect(next_url)

        LoginLog.objects.create(username=username, login_ip=user_ip, login_status=False)
        messages.error(request, "Invalid username or password.")
    context = {
        'form': form
    }
    return render(request, 'backend_login.html', context)


@login_required
def backend_logout(request):
    LoginLog.objects.create(
        user_id=request.user.id,
        username=request.user.username,
        login_ip=request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
        login_status=False
    )
    logout(request)
    return redirect('backend_login')


# Management Start
@method_decorator(admin_required, name='dispatch')
class UserListView(ListView):
    model = AdminUser
    template_name = 'user/list.html'
    context_object_name = 'user_list'
    ordering = ['created_at']
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "/backend/user/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset().select_related('user')
        full_name = self.request.GET.get('full_name', '')
        email = self.request.GET.get('email', '')
        phone = self.request.GET.get('phone', '')

        if full_name:
            queryset = queryset.filter(user__first_name__icontains=full_name)
        if email:
            queryset = queryset.filter(user__email__icontains=email)
        if phone:
            queryset = queryset.filter(phone__icontains=phone)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['full_name'] = self.request.GET.get('full_name', '')
        context['email'] = self.request.GET.get('email', '')
        context['phone'] = self.request.GET.get('phone', '')

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            get_params.pop('page')
        context['query_params'] = get_params.urlencode()

        return context


@admin_required
def user_add(request):
    if not checkUserPermission(request, "can_add", "/backend/user/"):
        return render(request, "403.html")

    if request.method == 'POST':
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New user has been added successfully!')
            return redirect('user_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreateForm()

    return render(request, 'user/add.html', {'form': form})


@admin_required
def user_update(request, data_id):
    if not checkUserPermission(request, "can_update", "/backend/user/"):
        return render(request, "403.html")

    # management = Area.objects.filter(unique_id=data_id).first()

    # if request.method == 'POST':
    #     select_country = request.POST.get('select_country')
    #     select_district = request.POST.get('select_district')
    #     select_sub_district = request.POST.get('select_sub_district')
    #     management_name = request.POST.get('management_name')

    #     if not select_country:
    #         messages.error(request, 'Please select country')
    #         return redirect('admin_app:management_update')

    #     country = Country.objects.filter(unique_id=select_country).first()
    #     if not country:
    #         messages.error(request, 'Country not found')
    #         return redirect('admin_app:management_update')

    #     if not select_district:
    #         messages.error(request, 'Please select district')
    #         return redirect('admin_app:management_update')

    #     district = District.objects.filter(unique_id=select_district, country=country).first()
    #     if not district:
    #         messages.error(request, 'District not found')
    #         return redirect('admin_app:management_update')

    #     if not select_sub_district:
    #         messages.error(request, 'Please select sub district')
    #         return redirect('admin_app:management_update')

    #     sub_district = SubDistrict.objects.filter(unique_id=select_sub_district, district=district).first()
    #     if not sub_district:
    #         messages.error(request, 'Sub district not found')
    #         return redirect('admin_app:management_update')

    #     if not management_name:
    #         messages.error(request, 'Please enter district name')
    #         return redirect('admin_app:management_update')

    #     if not management_name:
    #         messages.error(request, 'Please enter management name')
    #         return redirect('admin_app:management_update')

    #     if len(management_name) < 3:
    #         messages.warning(request, 'Area name must be at least 3 characters')
    #         return redirect('admin_app:management_update')

    #     if Area.objects.filter(name=management_name, sub_district=sub_district).exclude(id=management.id).exists():
    #         messages.warning(request, 'Area already exists')
    #         return redirect('admin_app:management_update')
    #     else:
    #         management.name = management_name
    #         management.sub_district_id = sub_district.id
    #         management.updated_by = request.user
    #         management.save()

    #         messages.success(request, 'Area added successfully')
    #         return redirect('admin_app:management_list')

    context = {
        # "management": management
    }
    return render(request, 'user/management_update.html', context)


@admin_required
def reset_password(request, data_id):
    if not checkUserPermission(request, "can_update", "/backend/user/"):
        return render(request, "403.html")

    user = get_object_or_404(AdminUser, id=data_id)
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user=user.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been updated successfully.')
            return redirect('backend_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AdminPasswordChangeForm(user=user.user)

    context = {
        'form': form,
        'user': user
    }
    return render(request, 'user/reset_password.html', context)


@admin_required
def user_permission(request, user_id):
    if not checkUserPermission(request, "can_update", "/backend/user-permission/"):
        return render(request, "403.html")

    if request.method == "POST":
        username = request.POST.get("username")
        user_status = request.POST.get("user_status")
        selected_menus = request.POST.getlist("selected_menus")
        can_view = request.POST.getlist("can_view")
        can_add = request.POST.getlist("can_add")
        can_update = request.POST.getlist("can_update")
        can_delete = request.POST.getlist("can_delete")

        try:
            user = User.objects.get(pk=user_id)
            user.is_active = user_status
            user.save()
        except Exception:
            pass

        exist_all_permission = UserMenuPermission.objects.filter(user_id=user_id)
        for exist_permission in exist_all_permission:
            if exist_permission.id not in selected_menus:
                exist_permission.can_view = False
                exist_permission.can_add = False
                exist_permission.can_update = False
                exist_permission.can_delete = False
                exist_permission.is_active = False
                exist_permission.updated_at = datetime.now()
                exist_permission.deleted_by_id = request.user.id
                exist_permission.save()

        if user_id and username and selected_menus:
            for menu_id in selected_menus:
                if menu_id in can_view:
                    user_view_access = True
                else:
                    user_view_access = False

                if menu_id in can_add:
                    user_add_access = True
                else:
                    user_add_access = False

                if menu_id in can_update:
                    user_update_access = True
                else:
                    user_update_access = False

                if menu_id in can_delete:
                    user_delete_access = True
                else:
                    user_delete_access = False

                exist_permission = UserMenuPermission.objects.filter(user_id=user_id, menu_id=menu_id)
                if exist_permission:
                    exist_permission.update(
                        updated_by_id=request.user.id, can_view=user_view_access, can_add=user_add_access,
                        can_update=user_update_access, can_delete=user_delete_access, updated_at=datetime.now(), is_active=True,
                    )
                else:
                    UserMenuPermission.objects.create(
                        user_id=user_id, menu_id=menu_id, can_view=user_view_access, can_add=user_add_access,
                        can_update=user_update_access, can_delete=user_delete_access, created_by_id=request.user.id
                    )
            messages.success(request, "User permission has been assigned!")
        else:
            messages.warning(request, "No permission has been assigned!")

        return redirect('user_permission', user_id=user_id)

    user = User.objects.get(pk=user_id)
    menu_list = BackendMenu.objects.filter(is_active=True).order_by("module_name")

    for data in menu_list:
        try:
            user_access_perm = UserMenuPermission.objects.get(user_id=user_id, menu_id=data.id, is_active=True)

            data.user_menu_id = user_access_perm.menu_id
            data.can_view = user_access_perm.can_view
            data.can_add = user_access_perm.can_add
            data.can_update = user_access_perm.can_update
            data.can_delete = user_access_perm.can_delete
        except Exception:
            pass

    context = {
        "user": user,
        "menu_list": menu_list,
    }
    return render(request, 'user/user_permission.html', context)
# Management User End


# Inventory
@admin_required
def inventory_dashboard(request):
    if not checkUserPermission(request, "can_view", "/backend/inventory/"):
        return render(request, "403.html")

    menu_list = UserMenuPermission.objects.filter(user_id=request.user.id, menu__parent_id=2, menu__is_sub_menu=True, can_view=True, menu__is_active=True, is_active=True, deleted=False).order_by('menu__id')

    for data in menu_list:
        sub_menu = UserMenuPermission.objects.filter(user_id=request.user.id, menu__parent_id=data.menu.id, menu__is_sub_child_menu=True, can_view=True, menu__is_active=True, is_active=True, deleted=False).order_by('menu__id')
        data.sub_menu = sub_menu

    context = {
        "menu_list": menu_list,
    }
    return render(request, 'inventory/inventory_dashboard.html', context)
# Inventory





# @login_required
# def setting_dashboard(request):
#     get_setting_menu = BackendMenu.objects.filter(module_name='Setting', is_active=True)
   
#     context = {
#         "get_setting_menu": get_setting_menu,
        
#     }
#     return render(request, 'home/setting_dashboard.html', context)





# @login_required
# def cities(request):
#     if not checkUserPermission(request, "can_view", "backend/cities/"):
#         return redirect('dashboard')

#     cities = City.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     cities, paginator_list, last_page_number = paginate_data(request, page_number, cities)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'cities': cities,
      
#     }
#     return render(request, "setting/city_list.html", context)





# @login_required
# def company_setting(request):
#     if not checkUserPermission(request, "can_view", "backend/company-setting/"):
#         return redirect('dashboard')

#     companies = Company.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     companies, paginator_list, last_page_number = paginate_data(request, page_number, companies)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'companies': companies,
#     }
#     return render(request, "setting/company/list.html", context)





# @login_required
# def add_new_company(request):
#     if not checkUserPermission(request, "can_add", "backend/add-new-company/"):
#         return redirect('dashboard')

#     if request.method == 'POST':
#         company_name = request.POST.get('company_name').strip()
#         company_address = request.POST.get('company_address').strip()
#         company_phone = request.POST.get('company_phone').strip()
#         company_email = request.POST.get('company_email').strip()

#         if not company_name or not company_address or not company_phone or not company_email:
#             messages.error(request, "All fields are required.")
#             return redirect('add_new_company')

#         Company.objects.create(
#             name=company_name,
#             address=company_address,
#             phone=company_phone,
#             email=company_email,
#             created_by=request.user.id
#         )
#         messages.success(request, "Company added successfully.")
#         return redirect('company_setting')

#     return render(request, "setting/company/add_company.html")





# #Products Information
# @login_required
# def product_main_category_list(request):
#     if not checkUserPermission(request, "can_view", "backend/product-main-category-list/"):
#         return redirect('dashboard')

    
#     product_main_categories = ProductMainCategory.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     product_main_categories, paginator_list, last_page_number = paginate_data(request, page_number, product_main_categories)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'product_main_categories': product_main_categories,
#     }
#     return render(request, "product/main_category_list.html", context)





# @login_required
# def add_product_main_category(request):
#     if not checkUserPermission(request, "can_add", "backend/add-product-main-category/"):
#         return redirect('dashboard')

#     if request.method == 'POST':
#         main_cat_name = request.POST.get('main_cat_name').strip()
#         description   = request.POST.get('description').strip()
#         cat_ordering  = request.POST.get('cat_ordering').strip()
#         cat_image     = request.FILES.get('cat_image')

#         if not main_cat_name:
#             messages.error(request, "Name is required.")
#             return redirect('add_product_main_category')

#         ProductMainCategory.objects.create(
#             main_cat_name=main_cat_name,
#             description=description,
#             cat_ordering=cat_ordering,
#             cat_image=cat_image,
#             is_active=True,
#             created_by=request.user
#         )
#         messages.success(request, "Product main category added successfully.")
#         return redirect('product_main_category_list')

#     form = ProductMainCategoryForm()
    
#     return render(request, "product/add_product_main_category.html", {'form': form})
   




# @login_required 
# def product_main_category_list_view(request):
#     """ 
#     View to list all active product main categories.
#     This view checks user permissions and paginates the list of product main categories.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     context  = {} 
#     if not checkUserPermission(request, "can_view", "backend/product-main-category-list/"):
#         return redirect('dashboard')

#     product_main_categories = ProductMainCategory.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     product_main_categories, paginator_list, last_page_number = paginate_data(request, page_number, product_main_categories)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'product_main_categories': product_main_categories,
#     }

#     return render(request, "product/maincategories/main_category_list.html", context)  




# @login_required
# def product_main_category_details_view(request, pk):
#     """ 
#     View to display the details of a specific product main category.
#     This view checks user permissions and retrieves the product main category by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {} 
#     if not checkUserPermission(request, "can_view", "backend/product-main-category-details/"):
#         return redirect('dashboard')
#     main_category_details = get_object_or_404(ProductMainCategory, pk=pk) 
#     context['main_category_details'] = main_category_details 
#     return render(request, 'product/maincategories/main_category_details.html', context) 




# @login_required
# def product_main_category_create_view(request):
#     """ 
#     View to create a new product main category.
#     This view checks user permissions and handles the form submission for creating a new product main category.
#     If the user does not have permission to add a new category, they are redirected to the dashboard.
#     """
#     context = {} 
#     if not checkUserPermission(request, "can_add", "backend/add-product-main-category/"):
#         return redirect('dashboard')
#     if request.method == "POST":
#         form = ProductMainCategoryForm(request.POST, request.FILES) 
#         if form.is_valid():
#             category = form.save(commit=False)
#             category.created_by = request.user
#             category.save()
#             messages.success(request, "Product main category created successfully.")
#             return redirect('product_main_category_list')
#     else:
#         form = ProductMainCategoryForm() 

#     context['form'] = form 
    
#     return render(request, 'product/maincategories/add_product_main_category.html', context)  





# @login_required
# def product_main_category_update_view(request, pk):
#     """ 
#     View to update an existing product main category.
#     This view checks user permissions and retrieves the product main category by its primary key (pk).
#     If the user does not have permission to update the category, they are redirected to the dashboard.
#     """
#     context = {} 
#     if not checkUserPermission(request, "can_edit", "backend/product-main-category-update/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductMainCategory, pk=pk) 
#     if request.method == "POST":
#         form = ProductMainCategoryForm(request.POST, request.FILES, instance=category) 
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Product main category updated successfully.")
#             return redirect('product_main_category_list')
#     else:
#         form = ProductMainCategoryForm(instance=category) 

#     context['form'] = form 
#     return render(request, 'product/maincategories/main_category_update.html', context) 




# @login_required
# def product_main_category_delete_view(request, pk):
#     """ 
#     View to delete a product main category.
#     This view checks user permissions and retrieves the product main category by its primary key (pk).
#     If the user does not have permission to delete the category, they are redirected to the dashboard.
#     """
#     if not checkUserPermission(request, "can_delete", "backend/delete-product-main-category/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductMainCategory, pk=pk) 
#     if request.method == "POST":
#         category.is_active = False
#         category.save()
#         messages.success(request, "Product main category deleted successfully.")
#         return redirect('product_main_category_list')
    
#     else:
#         messages.error(request, "You do not have permission to delete this category.")
#         return redirect('product_main_category_list') 
    

   


# @login_required
# def product_sub_category_list_view(request):
#     """ 
#     View to list all active product subcategories. 
#     This view checks user permissions and paginates the list of product subcategories.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     if not checkUserPermission(request, "can_view", "backend/product-sub-category-list/"):
#         return render(request, "403.html")

#     context = {}
#     product_sub_categories = ProductSubCategory.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     product_sub_categories, paginator_list, last_page_number = paginate_data(request, page_number, product_sub_categories)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'product_sub_categories': product_sub_categories,
#     }
#     return render(request, "product/subcategory/sub_category_list.html", context)
   



# @login_required
# def product_sub_category_details_view(request, pk):
#     """ 
#     View to display the details of a specific product subcategory.
#     This view checks user permissions and retrieves the product subcategory by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/product-sub-category-details/"):
#         return redirect('dashboard')
#     sub_category_details = get_object_or_404(ProductSubCategory, pk=pk)
#     context['sub_category_details'] = sub_category_details
#     return render(request, 'product/subcategory/sub_category_detail.html', context) 





# @login_required 
# def product_sub_category_create_view(request):
#     """ 
#     View to create a new product subcategory.
#     This view checks user permissions and handles the form submission for creating a new product subcategory.
#     If the user does not have permission to add a new category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_add", "backend/add-product-sub-category/"):
#         return redirect('dashboard')
    

#     opt_main_category  = ProductMainCategory.objects.filter(is_active=True).values('id', 'main_cat_name').order_by('-id')
    

#     if request.method == "POST":
#         main_category       = request.POST.get('main_category').strip()
#         sub_cat_name        = request.POST.get('sub_cat_name').strip()
#         sub_cat_slug        = request.POST.get('sub_cat_slug').strip()
#         description         = request.POST.get('description').strip()
#         sub_cat_image       = request.FILES.get('sub_cat_image')
#         sub_cat_ordering    = request.POST.get('sub_cat_ordering').strip() 

#         if not main_category or not sub_cat_name:
#             messages.error(request, 'Name is required') 
#             return redirect('add_product_sub_category')
        
#         try:
#             main_category_obj = ProductMainCategory.objects.get(id=main_category)
#             ProductSubCategory.objects.create(
#                 main_category    = main_category_obj, 
#                 sub_cat_name     = sub_cat_name, 
#                 description      = description, 
#                 sub_cat_image    = sub_cat_image, 
#                 sub_cat_ordering = int(sub_cat_ordering) if sub_cat_ordering else 0, 
#                 is_active        = True,
#                 created_by       = request.user, 
#             )
#             messages.success(request, "Product sub category created successfully.")
#             return redirect('product_sub_category_list')
#         except ProductMainCategory.DoesNotExist:
#             messages.error(request, 'Invalid main category selected') 
#             return redirect('add_product_sub_category')
#         except Exception as e:
#             messages.error(request, f'Error creating sub category: {str(e)}') 
#             return redirect('add_product_sub_category')
    
#     context['opt_main_category'] = opt_main_category
    
#     return render(request, 'product/subcategory/add_product_sub_category.html', context)
    



# def product_sub_category_update_view(request, pk):
#     """ 
#     View to update an existing product subcategory.
#     This view checks user permissions and retrieves the product subcategory by its primary key (pk).
#     If the user does not have permission to update the category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_edit", "backend/edit-product-sub-category/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductSubCategory, pk=pk)


#     opt_main_category = ProductMainCategory.objects.filter(is_active=True).values('id', 'main_cat_name').order_by('-id')

#     if request.method  == "POST":
#         main_category       = request.POST.get('main_category').strip() 
#         sub_cat_name        = request.POST.get('sub_cat_name').strip() 
#         sub_cat_slug        = request.POST.get('sub_cat_slug').strip() 
#         description         = request.POST.get('description').strip() 
#         sub_cat_image       = request.FILES.get('sub_cat_image') 
#         sub_cat_ordering    = request.POST.get('sub_cat_ordering').strip()
#         is_active           = request.POST.get('is_active') == 'on' 

#         if not main_category or not sub_cat_name:
#             messages.error(request, 'Name is required') 
#             return redirect('product_sub_category_update', pk=pk) 
    
#         try:
#             main_category_obj = ProductMainCategory.objects.get(id=main_category)
#             category.main_category    = main_category_obj
#             category.sub_cat_name     = sub_cat_name
#             category.sub_cat_slug     = sub_cat_slug if sub_cat_slug else category.sub_cat_slug
#             category.description      = description
#             if sub_cat_image:
#                 category.sub_cat_image = sub_cat_image
#             category.sub_cat_ordering = int(sub_cat_ordering) if sub_cat_ordering else 0
#             category.is_active        = is_active
#             category.updated_by       = request.user
#             category.save()
#             messages.success(request, "Product sub category updated successfully.")
#             return redirect('product_sub_category_list')
#         except ProductMainCategory.DoesNotExist:
#             messages.error(request, 'Invalid main category selected') 
#             return redirect('product_sub_category_update', pk=pk)
#         except Exception as e:
#             messages.error(request, f'Error updating sub category: {str(e)}') 
#             return redirect('product_sub_category_update', pk=pk)
        
#     context['opt_main_category'] = opt_main_category
#     context['category'] = category
    
#     return render(request, 'product/subcategory/sub_category_update.html', context) 




# @login_required  
# def product_sub_category_delete_view(request, pk):
#     """ 
#     View to delete a product subcategory.
#     This view checks user permissions and retrieves the product subcategory by its primary key (pk).
#     If the user does not have permission to delete the category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_delete", "backend/delete-product-sub-category/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductSubCategory, pk=pk)
#     if request.method == "POST":
#         category.is_active = False
#         category.save()
#         messages.success(request, "Product sub category deleted successfully.")
#         return redirect('product_sub_category_list')
#     else:
#         messages.error(request, "You do not have permission to delete this category.")
#         return redirect('product_sub_category_list') 
    
  



# @login_required
# def product_child_category_list_view(request):
#     """ 
#     View to list all active product child categories.
#     This view checks user permissions and paginates the list of product child categories.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/product-child-category-list/"):
#         return redirect('dashboard')

#     product_child_categories = ProductChildCategory.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     product_child_categories, paginator_list, last_page_number = paginate_data(request, page_number, product_child_categories)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'product_child_categories': product_child_categories,
#     }
#     return render(request, "product/chaildcategory/child_category_list.html", context)




# @login_required
# def product_child_category_details_view(request, pk):
#     """ 
#     View to display the details of a specific product child category.
#     This view checks user permissions and retrieves the product child category by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/product-child-category-details/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductChildCategory, pk=pk)
#     context['category'] = category
#     return render(request, 'product/chaildcategory/child_category_details.html', context) 





# @login_required
# def product_child_category_create_view(request):
#     """ 
#     View to create a new product child category.
#     This view checks user permissions and handles the form submission for creating a new product child category.
#     If the user does not have permission to add a new category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_add", "backend/add-product-child-category/"):
#         return redirect('dashboard')
    

#     opt_sub_category = ProductSubCategory.objects.filter(is_active=True).values('id', 'sub_cat_name').order_by('-id')

#     if request.method == "POST":
#         sub_cate_name       = request.POST.get('sub_cate_name').strip() 
#         child_cat_name      = request.POST.get('child_cat_name').strip() 
#         child_cat_slug      = request.POST.get('child_cat_slug').strip() 
#         description         = request.POST.get('description').strip() 
#         child_cat_ordering  = request.POST.get('child_cat_ordering').strip() 
#         child_cat_image     = request.FILES.get('child_cat_image') 


#         if not sub_cate_name or not child_cat_name:
#             messages.error(request, 'Name is required') 
#             return redirect('add_product_child_category') 
        

#         try:
#             sub_category_obj   = ProductSubCategory.objects.get(id=sub_cate_name) 
#             ProductChildCategory.objects.create(
#                 sub_category      = sub_category_obj, 
#                 child_cat_name    = child_cat_name, 
#                 description       = description, 
#                 child_cat_image   = child_cat_image, 
#                 child_cat_ordering= int(child_cat_ordering) if child_cat_ordering else 0, 
#                 is_active         = True,
#                 created_by        = request.user, 
#             )
#             messages.success(request, "Product child category created successfully.") 
#             return redirect('product_child_category_list') 
#         except ProductSubCategory.DoesNotExist:
#             messages.error(request, 'Invalid sub category selected') 
#             return redirect('add_product_child_category') 
#         except Exception as e:
#             messages.error(request, f'Error creating child category: {str(e)}') 
#             return redirect('add_product_child_category') 
        
#     context['opt_sub_category'] = opt_sub_category
#     return render(request, 'product/chaildcategory/add_child_category.html', context) 
    
       

    


# @login_required
# def product_child_category_update_view(request, pk):
#     """ 
#     View to update an existing product child category.
#     This view checks user permissions and retrieves the product child category by its primary key (pk).
#     If the user does not have permission to update the category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_edit", "backend/edit-product-child-category/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductChildCategory, pk=pk)

#     opt_sub_category = ProductSubCategory.objects.filter(is_active=True).values('id', 'sub_cat_name').order_by('-id') 

#     if request.method == "POST":
#         sub_cate_name       = request.POST.get('sub_cate_name').strip() 
#         child_cat_name      = request.POST.get('child_cat_name').strip() 
#         child_cat_slug      = request.POST.get('child_cat_slug').strip() 
#         description         = request.POST.get('description').strip() 
#         child_cat_image     = request.FILES.get('child_cat_image') 
#         child_cat_ordering  = request.POST.get('child_cat_ordering').strip() 

#         if not sub_cate_name or not child_cat_name:
#             messages.error(request, 'Name is required') 
#             return redirect('product_child_category_update', pk=pk) 
        
#         try:
#             sub_category_obj   = ProductSubCategory.objects.get(id=sub_cate_name) 
#             category.sub_category      = sub_category_obj
#             category.child_cat_name    = child_cat_name
#             category.child_cat_slug    = child_cat_slug if child_cat_slug else category.child_cat_slug
#             category.description       = description
#             if child_cat_image:
#                 category.child_cat_image = child_cat_image
#             category.child_cat_ordering= int(child_cat_ordering) if child_cat_ordering else 0
#             category.is_active         = True
#             category.updated_by        = request.user
#             category.save()
#             messages.success(request, "Product child category updated successfully.")
#             return redirect('product_child_category_list')
#         except ProductSubCategory.DoesNotExist:
#             messages.error(request, 'Invalid sub category selected') 
#             return redirect('product_child_category_update', pk=pk)
#         except Exception as e:
#             messages.error(request, f'Error updating child category: {str(e)}') 
#             return redirect('product_child_category_update', pk=pk)
        
#     context['opt_sub_category'] = opt_sub_category 
#     context['category'] = category
#     return render(request, 'product/chaildcategory/child_category_update.html', context) 
        





# @login_required
# def product_child_category_delete_view(request, pk):
#     """ 
#     View to delete a product child category.
#     This view checks user permissions and retrieves the product child category by its primary key (pk).
#     If the user does not have permission to delete the category, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_delete", "backend/delete-product-child-category/"):
#         return redirect('dashboard')
#     category = get_object_or_404(ProductChildCategory, pk=pk)
#     if request.method == "POST":
#         category.is_active = False
#         category.save()
#         messages.success(request, "Product child category deleted successfully.")
#         return redirect('product_child_category_list')
#     else:
#         messages.error(request, "You do not have permission to delete this category.")
#         return redirect('product_child_category_list') 
    
   



# @login_required 
# def attribute_list_view(request):
#     """ 
#     View to list all active attributes.
#     This view checks user permissions and paginates the list of attributes.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-list/"):
#         return redirect('dashboard')

#     attributes = AttributeList.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     attributes, paginator_list, last_page_number = paginate_data(request, page_number, attributes)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'attributes': attributes,
#     }
#     return render(request, "product/attribute_list.html", context)




# @login_required
# def attribute_details_view(request, pk):
#     """ 
#     View to display the details of a specific attribute.
#     This view checks user permissions and retrieves the attribute by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-details/"):
#         return redirect('dashboard')
#     attribute = get_object_or_404(AttributeList, pk=pk)
#     context['attribute'] = attribute
#     return render(request, 'product/', context) 



# @login_required
# def attribute_create_view(request):
#     """ 
#     View to create a new attribute.
#     This view checks user permissions and handles the form submission for creating a new attribute.
#     If the user does not have permission to add a new attribute, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_add", "backend/add-attribute/"):
#         return redirect('dashboard')
#     if request.method == "POST":
#         form = AttributeListForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Attribute created successfully.")
#             return redirect('attribute_list')
#     else:
#         form = AttributeListForm()

#     context['form'] = form
    
#     return render(request, 'product/', context) 




# @login_required
# def attribute_update_view(request, pk):
#     """ 
#     View to update an existing attribute.
#     This view checks user permissions and retrieves the attribute by its primary key (pk).
#     If the user does not have permission to update the attribute, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_edit", "backend/edit-attribute/"):
#         return redirect('dashboard')
#     attribute = get_object_or_404(AttributeList, pk=pk)
#     if request.method == "POST":
#         form = AttributeListForm(request.POST, instance=attribute)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Attribute updated successfully.")
#             return redirect('attribute_list')
#     else:
#         form = AttributeListForm(instance=attribute)

#     context['form'] = form
#     return render(request, 'product/', context) 



# @login_required
# def attribute_delete_view(request, pk):
#     """ 
#     View to delete an attribute.
#     This view checks user permissions and retrieves the attribute by its primary key (pk).
#     If the user does not have permission to delete the attribute, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_delete", "backend/delete-attribute/"):
#         return redirect('dashboard')
#     attribute = get_object_or_404(AttributeList, pk=pk)
#     if request.method == "POST":
#         attribute.is_active = False
#         attribute.save()
#         messages.success(request, "Attribute deleted successfully.")
#         return redirect('attribute_list')
    
#     context['attribute'] = attribute
#     return render(request, 'product/', context) 




# @login_required
# def attribute_value_list_view(request):
#     """ 
#     View to list all active attribute values.
#     This view checks user permissions and paginates the list of attribute values.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-value-list/"):
#         return redirect('dashboard')

#     attribute_values = AttributeValueList.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     attribute_values, paginator_list, last_page_number = paginate_data(request, page_number, attribute_values)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'attribute_values': attribute_values,
#     }
#     return render(request, "product/attribute_value_list.html", context) 




# @login_required
# def attribute_value_details_view(request, pk):
#     """ 
#     View to display the details of a specific attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-value-details/"):
#         return redirect('dashboard')
#     attribute_value = get_object_or_404(AttributeValueList, pk=pk)
#     context['attribute_value'] = attribute_value
#     return render(request, 'product/', context) 





# @login_required
# def attribute_value_create_view(request):
#     """ 
#     View to create a new attribute value.
#     This view checks user permissions and handles the form submission for creating a new attribute value.
#     If the user does not have permission to add a new attribute value, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_add", "backend/add-attribute-value/"):
#         return redirect('dashboard')
#     if request.method == "POST":
#         form = AttributeValueListForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Attribute value created successfully.")
#             return redirect('attribute_value_list')
#     else:
#         form = AttributeValueListForm()

#     context['form'] = form
    
#     return render(request, 'product/', context)





# @login_required
# def attribute_value_update_view(request, pk):
#     """ 
#     View to update an existing attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to update the attribute value, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_edit", "backend/edit-attribute-value/"):
#         return redirect('dashboard')
#     attribute_value = get_object_or_404(AttributeValueList, pk=pk)
#     if request.method == "POST":
#         form = AttributeValueListForm(request.POST, instance=attribute_value)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Attribute value updated successfully.")
#             return redirect('attribute_value_list')
#     else:
#         form = AttributeValueListForm(instance=attribute_value)

#     context['form'] = form
#     return render(request, 'product/', context)




# @login_required
# def attribute_value_delete_view(request, pk):
#     """ 
#     View to delete an attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to delete the attribute value, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_delete", "backend/delete-attribute-value/"):
#         return redirect('dashboard')
#     attribute_value = get_object_or_404(AttributeValueList, pk=pk)
#     if request.method == "POST":
#         attribute_value.is_active = False
#         attribute_value.save()
#         messages.success(request, "Attribute value deleted successfully.")
#         return redirect('attribute_value_list')
    
#     context['attribute_value'] = attribute_value
#     return render(request, 'product/', context)