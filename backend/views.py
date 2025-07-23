import pandas as pd 
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.utils import timezone 

from datetime import datetime
from urllib.parse import urlencode

from backend.common_func import checkUserPermission
from backend.decorators import admin_required
from backend.models import (
    LoginLog, AdminUser, BackendMenu, UserMenuPermission, FrontendSettings, EmailConfiguration, SMSLog, SMSConfiguration, ProductBrand,
    ProductMainCategory, ProductSubCategory, ProductChildCategory, AttributeList, AttributeValueList, ProductList, ProductAttribute
)
from backend.forms import (
    CustomUserLoginForm, UserCreateForm, FrontendSettingsForm, EmailConfigurationForm, SMSConfigurationForm, ProductBrandForm,
    ProductMainCategoryForm, ProductSubCategoryForm, ProductChildCategoryForm, AttributeListForm, AttributeValueListForm,
    ProductListForm, ProductAttributeForm
)

from backend.export_excel import export_data_to_excel 
from backend.get_fks_kes_instance import get_foreign_key_instance 


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
        return redirect('backend:dashboard')

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

                next_url = request.GET.get('next', reverse('backend:backend_dashboard'))
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
    return redirect('backend:backend_login')


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
        username = self.request.GET.get('username', '')
        is_active = self.request.GET.get('is_active', '')

        if username:
            queryset = queryset.filter(user__username__icontains=username)
        if is_active:
            queryset = queryset.filter(user__is_active=is_active)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.GET.get('username', '')
        context['is_active'] = self.request.GET.get('is_active', '')

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            get_params.pop('page')
        context['query_params'] = get_params.urlencode()

        context['filter_user'] = AdminUser.objects.all()

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
            return redirect('backend:user_list')
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
            return redirect('backend:backend_dashboard')
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

        return redirect('backend:user_permission', user_id=user_id)

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


@method_decorator(login_required, name='dispatch')
class BrandListView(ListView):
    model = ProductBrand
    template_name = 'product/brand/brand_list.html'
    paginated_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_view', 'backend/brand/'):
            return render(request, '403.html')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return ProductBrand.objects.filter(is_active=True).order_by('-id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_query = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_query)

        context.update({
            'brand_list': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number
        })
        return context


@login_required
def brand_detail_view(request, pk):
    if not checkUserPermission(request, 'can_view', 'backend/brand/'):
        messages.error(request, 'You have not permission to view')
        return render(request, '403.html')

    brand = get_object_or_404(ProductBrand, pk=pk)
    context = {
        'brand': brand
    }
    return render(request, 'product/brand/brand_detail.html', context)


@method_decorator(login_required, name='dispatch')
class BrandCreateView(CreateView):
    model = ProductBrand
    form_class = ProductBrandForm
    template_name = 'product/brand/add_brand.html'
    success_url = reverse_lazy('backend:brand_list')
 
    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_add', 'backend/brand/'):
            messages.error(request, 'You have not permision to add brand ')
            return render(request, '403.html')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BrandUpdateView(UpdateView):
    model = ProductBrand
    form_class = ProductBrandForm
    template_name = 'product/brand/update_brand.html'
    success_url = reverse_lazy('backend:brand_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_update', 'backend/brand/'):
            messages.error(request, 'You do not have permission to update this brand.')
            return render(request, '403.html')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Brand updated successfully.')
        return super().form_valid(form)


@login_required
def brand_delete_view(request, pk):
    if not checkUserPermission(request, 'can_delete', 'backend/brand'):
        return render(request, '403.html')
    
    brand = get_object_or_404(ProductBrand, pk=pk)

    if request.method == 'POST':
        brand.is_active = False
        brand.save()
        messages.success(request, 'Product brand deleted successfully!')
        return redirect('backend:brand_list')

    return redirect('backend:brand_list')


@method_decorator(login_required, name='dispatch')
class MainCategoryListView(ListView):
    model = ProductMainCategory
    template_name = 'product/maincategories/main_cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/category/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        filters = {'is_active': True}

        main_category_id     = self.request.GET.get('name')
        created_from         = self.request.GET.get('created_from')
        created_to           = self.request.GET.get('created_to') 
    
        if main_category_id:
            filters['id'] = main_category_id
        if created_from:
            filters['created_at__date__gte'] = created_from
        if created_to:
            filters['created_at__date__lte'] = created_to

        return ProductMainCategory.objects.filter(**filters).order_by('-id')
    
    def get(self, request, *args, **kwargs):
        if self.request.GET.get('export') == 'excel':
            queryset    = self.get_queryset()
            headers     = ['ID', 'Name', 'Description', 'Created at', 'Status' ]

            rows = [] 
            for row in queryset:
                rows.append([
                    row.id,
                    row.name,
                    row.description,
                    row.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Active' if row.is_active else 'Inactive'
                ])
            filename = 'maincategory'
            return export_data_to_excel(filename=filename, heaers=headers, rows=rows)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

       

        context.update({
            'product_main_categories': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            get_params.pop('page')
        context['query_params'] = get_params.urlencode()

        return context
    

@login_required
def category_detail_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/category/"):
        messages.error(request, "You do not have permission to view this product main category.")
        return render(request, "403.html")

    main_category_details = get_object_or_404(ProductMainCategory, pk=pk)
    
    context = {
        'main_category_details': main_category_details
    }
    return render(request, 'product/maincategories/cat_details.html', context)


@method_decorator(login_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = ProductMainCategory
    form_class = ProductMainCategoryForm
    template_name = 'product/maincategories/add_category.html'
    success_url = reverse_lazy('backend:category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/category/"):
            messages.error(request, "You do not have permission to add a product main category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product main category created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = ProductMainCategory
    form_class = ProductMainCategoryForm
    template_name = 'product/maincategories/update_category.html'
    success_url = reverse_lazy('backend:category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_update", "backend/category/"):
            messages.error(request, "You do not have permission to update this product main category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product main category updated successfully.")
        return super().form_valid(form)
    

@login_required
def category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/category/"):
        return render(request, "403.html")

    category = get_object_or_404(ProductMainCategory, pk=pk)

    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, "Product main category deleted successfully.")
        return redirect('backend:category_list')

    return redirect('backend:category_list')


@method_decorator(login_required, name='dispatch')
class SubCategoryListView(ListView):
    model = ProductSubCategory
    template_name = 'product/subcategories/cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/sub-category/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ProductSubCategory.objects.filter(is_active=True).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'product_sub_categories': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })
        return context
    

@login_required
def sub_category_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/sub-category/"):
        messages.error(request, "You do not have permission to view this product sub category.")
        return render(request, "403.html")

    sub_category_details = get_object_or_404(ProductSubCategory, pk=pk)

    context = {
        'sub_category_details': sub_category_details
    }
    return render(request, 'product/subcategories/cat_details.html', context)


@method_decorator(login_required, name='dispatch')
class SubCategoryCreateView(CreateView):
    model = ProductSubCategory
    form_class = ProductSubCategoryForm
    template_name = 'product/subcategories/add_category.html'
    success_url = reverse_lazy('backend:sub_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/sub-category/"):
            messages.error(request, "You do not have permission to add a product sub category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product sub category created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class SubCategoryUpdateView(UpdateView):
    model = ProductSubCategory
    form_class = ProductSubCategoryForm
    template_name = 'product/subcategories/cat_update.html'
    success_url = reverse_lazy('backend:sub_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_update", "backend/sub-category/"):
            messages.error(request, "You do not have permission to update this product sub category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product sub category updated successfully.")
        return super().form_valid(form)
    

@login_required
def sub_category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/sub-category/"):
        return render(request, "403.html")

    sub_category = get_object_or_404(ProductSubCategory, pk=pk)

    if request.method == 'POST':
        sub_category.is_active = False
        sub_category.save()
        messages.success(request, "Product sub category deleted successfully.")
        return redirect('backend:sub_category_list')

    return redirect('backend:sub_category_list')


class ChildCategoryListView(ListView):
    model = ProductChildCategory
    template_name = 'product/childcategories/cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/child-category"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ProductChildCategory.objects.filter(is_active=True).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'product_child_categories': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })
        return context


@login_required
def child_category_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/child-category/"):
        messages.error(request, "You do not have permission to view this product child category.")
        return render(request, "403.html")

    child_category_details = get_object_or_404(ProductChildCategory, pk=pk)

    context = {
        'child_category_details': child_category_details
    }
    return render(request, 'product/childcategories/cat_details.html', context)


class ChildCategoryCreateView(CreateView):
    model = ProductChildCategory
    form_class = ProductChildCategoryForm
    template_name = 'product/childcategories/add_category.html'
    success_url = reverse_lazy('backend:child_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/child-category"):
            messages.error(request, "You do not have permission to add a product child category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product child category created successfully.")
        return super().form_valid(form)


class ChildCategoryUpdateView(UpdateView):
    model = ProductChildCategory
    form_class = ProductChildCategoryForm
    template_name = 'product/childcategories/cat_update.html'
    success_url = reverse_lazy('backend:child_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_edit", "backend/child-category"):
            messages.error(request, "You do not have permission to update this product child category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product child category updated successfully.")
        return super().form_valid(form)


@login_required
def child_category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/child-category/"):
        return render(request, "403.html")

    child_category = get_object_or_404(ProductChildCategory, pk=pk)

    if request.method == 'POST':
        child_category.is_active = False
        child_category.save()
        messages.success(request, "Product child category deleted successfully.")
        return redirect('backend:child_category_list')

    return redirect('backend:child_category_list')


@method_decorator(login_required, name='dispatch')
class AttributeListView(ListView):
    model = AttributeList
    template_name = 'product/attributes/attribute_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/attributes/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AttributeList.objects.filter(is_active=True).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'attribute_lists': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })
        return context


@login_required
def attribute_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/attributes/"):
        messages.error(request, "You do not have permission to view this attribute.")
        return render(request, "403.html")

    attribute_details = get_object_or_404(AttributeList, pk=pk)

    context = {
        'attribute_details': attribute_details
    }
    return render(request, 'product/attributes/attribute_details.html', context)


@method_decorator(login_required, name='dispatch')
class AttributeCreateView(CreateView):
    model = AttributeList
    form_class = AttributeListForm
    template_name = 'product/attributes/add_attribute.html'
    success_url = reverse_lazy('backend:attribute_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/attributes/"):
            messages.error(request, "You do not have permission to add an attribute.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Attribute created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AttributeUpdateView(UpdateView):
    model = AttributeList
    form_class = AttributeListForm
    template_name = 'product/attributes/attribute_update.html'
    success_url = reverse_lazy('backend:attribute_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_edit", "backend/attributes/"):
            messages.error(request, "You do not have permission to update this attribute.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Attribute updated successfully.")
        return super().form_valid(form)


@login_required
def attribute_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/attributes/"):
        return render(request, "403.html")

    attribute = get_object_or_404(AttributeList, pk=pk)

    if request.method == 'POST':
        attribute.is_active = False
        attribute.save()
        messages.success(request, "Attribute deleted successfully.")
        return redirect('backend:attribute_list')

    return redirect('backend:attribute_list')


@method_decorator(login_required, name='dispatch')
class AttributeValueListView(ListView):
    model = AttributeValueList
    template_name = 'product/attributevalue/value_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/attribute-value-list/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return AttributeValueList.objects.filter(is_active=True).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'value_lists': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })
        return context


@login_required
def value_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/attribute-value-details/"):
        messages.error(request, "You do not have permission to view this attribute value.")
        return render(request, "403.html")

    value_details = get_object_or_404(AttributeValueList, pk=pk)

    context = {
        'value_details': value_details
    }
    return render(request, 'product/attributevalue/value_details.html', context)


@method_decorator(login_required, name='dispatch')
class AttributeValueCreateView(CreateView):
    model = AttributeValueList
    form_class = AttributeValueListForm
    template_name = 'product/attributevalue/add_value.html'
    success_url = reverse_lazy('backend:value_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/attribute-value-list/"):
            messages.error(request, "You do not have permission to add an attribute value.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Attribute value created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class AttributeValueUpdateView(UpdateView):
    model = AttributeValueList
    form_class = AttributeValueListForm
    template_name = 'product/attributevalue/value_update.html'
    success_url = reverse_lazy('backend:value_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_edit", "backend/attribute-value-list/"):
            messages.error(request, "You do not have permission to update this attribute value.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Attribute value updated successfully.")
        return super().form_valid(form)


@login_required
def value_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/attribute-value-delete/"):
        return render(request, "403.html")

    value = get_object_or_404(AttributeValueList, pk=pk)

    if request.method == 'POST':
        value.is_active = False
        value.save()
        messages.success(request, "Attribute value deleted successfully.")
        return redirect('backend:value_list')

    return redirect('backend:value_list')


@method_decorator(login_required, name='dispatch')
class ProductListView(ListView):
    model = ProductList
    template_name = 'product/products/product_list.html'
    # template_name = 'product/pdf/pdf_template.html'   # for pdf template editing 
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/products/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        filters = {'deleted': False}

        product_id = self.request.GET.get('product')
        brand_id = self.request.GET.get('brand')
        category_id = self.request.GET.get('category')
        sub_category_id = self.request.GET.get('sub_category')
        child_category_id = self.request.GET.get('child_category')
        created_from = self.request.GET.get('created_from')
        created_to = self.request.GET.get('created_to')

        if created_from:
            filters['created_at__gte'] = created_from
        if created_to:
            filters['created_at__lte'] = created_to

        if product_id:
            filters['id'] = product_id
        if brand_id:
            filters['brand__id'] = brand_id
        if category_id:
            filters['main_category__id'] = category_id
        if sub_category_id:
            filters['sub_category__id'] = sub_category_id
        if child_category_id:
            filters['child_category__id'] = child_category_id
        
        return ProductList.objects.filter(**filters).order_by('-id')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = int(self.request.GET.get('page', 1))
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'products': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,

            'filter_created_from': self.request.GET.get('created_from', ''),
            'filter_created_to': self.request.GET.get('created_to', ''),
            'filter_product_id': self.request.GET.get('product', ''),
            'filter_brand': self.request.GET.get('brand', ''),
            'filter_category': self.request.GET.get('category', ''),
            'filter_sub_ategory': self.request.GET.get('sub_category', ''),
            'filter_child_category': self.request.GET.get('child_category', ''),
            'filter_products': ProductList.objects.filter(is_active=True).order_by('product_name'),
            'filter_brands': ProductBrand.objects.filter(is_active=True).order_by('name'),
            'filter_categories': ProductMainCategory.objects.filter(is_active=True).order_by('name'),
            'filter_sub_categories': ProductSubCategory.objects.filter(is_active=True).order_by('name'),
            'filter_child_categories': ProductChildCategory.objects.filter(is_active=True).order_by('name'),
            'sl_start': (page_num - 1) * paginated_data.paginator.per_page,
        })

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            get_params.pop('page')
        context['query_params'] = get_params.urlencode()

        return context
    

def upload_product_excel(request):
    if not checkUserPermission(request, 'can_add', 'backend/product/'):
        messages.error(request, "You do not have permission to upload excel sheet")
        return render(request, '403.html')
    
    log = {
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'details': {
            'missing_required_fields': [],
            'invalid_foreign_keys': [],
            'missing_created_by': [],
            'duplicate_sku': [],
            'other_errors': []
        }
    }

    if request.method == "POST":
        product_excel_sheet = request.FILES.get('excel-sheet')

        if product_excel_sheet:
            try:
                df = pd.read_excel(product_excel_sheet)
                required_fields = ['product_name', 'product_sku', 'brand', 'main_category', 'created_by']

                for index, row in df.iterrows():
                    row_num = index + 2
                    missing_fields = []
                    fk_issues = []

                    for field in required_fields:
                        if pd.isna(row.get(field)) or str(row.get(field)).strip() == '':
                            missing_fields.append(field)

                    if missing_fields:
                        log['details']['missing_required_fields'].append({'row': row_num, 'columns': missing_fields})
                        log['skipped'] += 1
                        continue

                    sku = str(row.get('product_sku')).strip()

                    if not sku:
                        log['details']['missing_required_fields'].append({'row': row_num, 'columns': ['product_sku']})
                        log['skipped'] += 1
                        continue

                    try:
                        """ 
                        Check for foreign key instances and collect issues 
                        
                        """
                        brand, _           = get_foreign_key_instance(ProductBrand, row.get('brand'), 'Brand', fk_issues, row_num, required=True)
                        main_cat, _        = get_foreign_key_instance(ProductMainCategory, row.get('main_category'), 'Main Category', fk_issues, row_num, required=True)
                        sub_cat, _         = get_foreign_key_instance(ProductSubCategory, row.get('sub_category'), 'Sub Category', fk_issues, row_num)
                        child_cat, _       = get_foreign_key_instance(ProductChildCategory, row.get('child_category'), 'Child Category', fk_issues, row_num)
                        created_by_user, _ = get_foreign_key_instance(User, row.get('created_by'), 'Created By User', fk_issues, row_num, required=True)

                        if not created_by_user:
                            log['details']['missing_created_by'].append({'row': row_num, 'reason': f"User with ID '{row.get('created_by')}' not found."})
                            log['skipped'] += 1
                            continue

                        if fk_issues:
                            log['details']['invalid_foreign_keys'].append({'row': row_num, 'issues': fk_issues})
                            log['failed'] += 1
                            continue

                        product_exists = ProductList.objects.filter(product_sku=sku).exists()

                        defaults = {
                            'product_name': row.get('product_name'),
                            'brand': brand,
                            'main_category': main_cat,
                            'sub_category': sub_cat,
                            'child_category': child_cat,
                            'short_description': row.get('short_description') or '',
                            'description': row.get('description') or '',
                            'unit_price': float(row.get('unit_price', 0)),
                            'sale_price': float(row.get('sale_price', 0)),
                            'discount_status': bool(row.get('discount_status')),
                            'discount_percent': int(row.get('discount_percent', 0)),
                            'discount_price': float(row.get('discount_price', 0)),
                            'total_qty': int(row.get('total_qty', 0)),
                            'sold_qty': int(row.get('sold_qty', 0)),
                            'return_qty': int(row.get('return_qty', 0)),
                            'available_qty': int(row.get('available_qty', 0)),
                            'stock_status': row.get('stock_status') if row.get('stock_status') in ['In Stock', 'Stock Out'] else 'In Stock',
                            'product_ordering': int(row.get('product_ordering', 0)),
                            'total_views': int(row.get('total_views', 0)),
                            'is_new_product': bool(row.get('is_new_product')),
                            'is_featured_product': bool(row.get('is_featured_product')),
                            'is_combo_product': bool(row.get('is_combo_product')),
                            'created_by': created_by_user,
                            'updated_by': created_by_user,
                            'updated_at': timezone.now(),
                            'is_active': bool(row.get('is_active')) if pd.notna(row.get('is_active')) else True,
                            'deleted': bool(row.get('deleted')) if pd.notna(row.get('deleted')) else False,
                        }

                        product, created = ProductList.objects.update_or_create(
                            product_sku=sku,
                            defaults=defaults
                        )

                        if created:
                            log['inserted'] += 1
                        elif product_exists:
                            log['updated'] += 1

                    except Exception as row_err:
                        log['details']['other_errors'].append(f"Row {row_num}: Error - {str(row_err)}")
                        log['skipped'] += 1
                        continue

            except Exception as e:
                log['details']['other_errors'].append(f"File-level Error: {str(e)}")

    if log['inserted'] > 0:
        messages.success(request, f"Successfully inserted {log['inserted']} products.")
    if log['updated'] > 0:
        messages.info(request, f"Successfully updated {log['updated']} products.")
    if log['skipped'] > 0:
        messages.warning(request, f"{log['skipped']} products were skipped due to issues.")
    if log['failed'] > 0:
        messages.error(request, f"{log['failed']} products failed to process.")
    if log['details']['other_errors']:
        messages.error(request, f"Unexpected errors occurred. Please review the logs.")

    return render(request, 'product/products/upload_excel.html', {'log': log})




@login_required
def product_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/products/"):
        messages.error(request, "You do not have permission to view this product.")
        return render(request, "403.html")

    product_details = get_object_or_404(ProductList, pk=pk)

    context = {
        'product_details': product_details
    }
    return render(request, 'product/products/product_details.html', context)


@method_decorator(login_required, name='dispatch')
class ProductCreateView(CreateView):
    model = ProductList
    form_class = ProductListForm
    template_name = 'product/products/add_product.html'
    success_url = reverse_lazy('backend:product_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/products/"):
            messages.error(request, "You do not have permission to add a product.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class ProductUpdateView(UpdateView):
    model = ProductList
    form_class = ProductListForm
    template_name = 'product/products/product_update.html'
    success_url = reverse_lazy('backend:product_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_update", "backend/products/"):
            messages.error(request, "You do not have permission to update this product.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)
    

@login_required
def product_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/products/"):
        return render(request, "403.html")

    product = get_object_or_404(ProductList, pk=pk)

    if request.method == 'POST':
        product.deleted = True
        product.save()
        messages.success(request, "Product deleted successfully.")
        return redirect('backend:product_list')

    return redirect('backend:product_list')


@method_decorator(login_required, name='dispatch')
class ProductAttibuteListView(ListView):
    model = ProductAttribute
    template_name = 'product/productattrs/attribute_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/product-attribute-list/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return ProductAttribute.objects.filter(is_active=True).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'product_attributes': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,
        })
        return context


@login_required
def product_attribute_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/product-attribute-details/"):
        messages.error(request, "You do not have permission to view this product attribute.")
        return render(request, "403.html")

    product_attribute_details = get_object_or_404(ProductAttribute, pk=pk)

    context = {
        'product_attribute_details': product_attribute_details
    }
    return render(request, 'product/productattrs/attribute_details.html', context)


@method_decorator(login_required, name='dispatch')
class ProductAttributeCreateView(CreateView):
    model = ProductAttribute
    form_class = ProductAttributeForm
    template_name = 'product/productattrs/add_attribute.html'
    success_url = reverse_lazy('backend:product_attribute_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/product-attribute-list/"):
            messages.error(request, "You do not have permission to add a product attribute.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product attribute created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductAttributeUpdateView(UpdateView):
    model = ProductAttribute
    form_class = ProductAttributeForm
    template_name = 'product/productattrs/attribute_update.html'
    success_url = reverse_lazy('backend:product_attribute_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_edit", "backend/product-attribute-list/"):
            messages.error(request, "You do not have permission to update this product attribute.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product attribute updated successfully.")
        return super().form_valid(form)


@login_required
def product_attribute_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/product-attribute-delete/"):
        return render(request, "403.html")

    product_attribute = get_object_or_404(ProductAttribute, pk=pk)

    if request.method == 'POST':
        product_attribute.is_active = False
        product_attribute.save()
        messages.success(request, "Product attribute deleted successfully.")
        return redirect('backend:product_attribute_list')

    return redirect('backend:product_attribute_list')


# Settings
@admin_required
def setting_dashboard(request):
    if not checkUserPermission(request, "can_view", "/backend/settings/"):
        return render(request, "403.html")

    menu_list = UserMenuPermission.objects.filter(user_id=request.user.id, menu__parent_id=6, menu__is_sub_menu=True, can_view=True, menu__is_active=True, is_active=True, deleted=False).order_by('menu__id')

    for data in menu_list:
        sub_menu = UserMenuPermission.objects.filter(user_id=request.user.id, menu__parent_id=data.menu.id, menu__is_sub_child_menu=True, can_view=True, menu__is_active=True, is_active=True, deleted=False).order_by('menu__id')
        data.sub_menu = sub_menu

    context = {
        "menu_list": menu_list,
    }
    return render(request, 'setting/setting_dashboard.html', context)


@admin_required
def website_setting(request):
    if not checkUserPermission(request, "can_view", "/backend/website-setting/"):
        return render(request, "403.html")

    instance = FrontendSettings.objects.first()

    if request.method == 'POST':
        form = FrontendSettingsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            settings = form.save(commit=False)
            if not instance:
                settings.created_by = request.user
            else:
                settings.updated_by = request.user
                settings.updated_at = datetime.now()
            settings.save()
            return redirect('backend:website_setting')
    else:
        form = FrontendSettingsForm(instance=instance)

    return render(request, 'setting/website_setting.html', {'form': form})


class EmailConfigurationCreateUpdateView(CreateView):
    template_name = 'setting/email_configuration.html'

    def get_object(self):
        return EmailConfiguration.objects.filter(is_active=True).first()

    def get(self, request):
        obj = self.get_object()
        can_add = checkUserPermission(request, "can_add", "/backend/email-configuration/")
        can_update = checkUserPermission(request, "can_update", "/backend/email-configuration/")
        read_only = not (can_add or can_update)
        form = EmailConfigurationForm(instance=obj, read_only=read_only)

        if read_only:
            messages.error(request, "You do not have permission to edit this configuration.")

        context = {
            "form": form,
            "read_only": read_only,
            "object": obj,
            "can_add": can_add,
            "can_update": can_update,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        obj = self.get_object()
        can_add = checkUserPermission(request, "can_add", "/hr/email-configuration/")
        can_update = checkUserPermission(request, "can_update", "/hr/email-configuration/")
        read_only = not (can_add or can_update)

        if read_only:
            messages.error(request, "You do not have permission to edit this configuration.")
            return redirect(reverse("backend:email_configuration_create_update"))

        if obj:
            form = EmailConfigurationForm(request.POST, instance=obj)
        else:
            form = EmailConfigurationForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            if obj:
                instance.updated_by = request.user
                instance.updated_at = datetime.now()
            else:
                instance.created_by = request.user
            instance.status = True
            instance.save()
            messages.success(request, "Email Configuration saved successfully.")
            return redirect(reverse("backend:email_configuration_create_update"))

        context = {
            "form": form,
            "read_only": False,
            "object": obj,
            "can_add": can_add,
            "can_update": can_update,
        }
        return render(request, self.template_name, context)


class SMSConfigurationCreateUpdateView(CreateView):
    template_name = 'setting/sms_configuration.html'

    def get_object(self):
        return SMSConfiguration.objects.filter(status=True).first()

    def get(self, request):
        obj = self.get_object()
        can_add = checkUserPermission(request, "can_add", "/backend/sms-configuration/")
        can_update = checkUserPermission(request, "can_update", "/backend/sms-configuration/")
        read_only = not (can_add or can_update)
        form = SMSConfigurationForm(instance=obj, read_only=read_only)

        if read_only:
            messages.error(request, "You do not have permission to edit this configuration.")

        context = {
            "form": form,
            "read_only": read_only,
            "object": obj,
            "can_add": can_add,
            "can_update": can_update,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        obj = self.get_object()
        can_add = checkUserPermission(request, "can_add", "/backend/sms-configuration/")
        can_update = checkUserPermission(request, "can_update", "/backend/sms-configuration/")
        read_only = not (can_add or can_update)

        if read_only:
            messages.error(request, "You do not have permission to edit this configuration.")
            return redirect(reverse("backend:sms_configuration_create_update"))

        if obj:
            form = SMSConfigurationForm(request.POST, instance=obj)
        else:
            form = SMSConfigurationForm(request.POST)

        if form.is_valid():
            instance = form.save(commit=False)
            if obj:
                instance.updated_by = request.user
                instance.updated_at = datetime.now()
            else:
                instance.created_by = request.user
            instance.status = True
            instance.save()
            messages.success(request, "SMS Configuration saved successfully.")
            return redirect(reverse("backend:sms_configuration_create_update"))

        context = {
            "form": form,
            "read_only": False,
            "object": obj,
            "can_add": can_add,
            "can_update": can_update,
        }
        return render(request, self.template_name, context)


@login_required
def sent_sms_list(request):
    if not checkUserPermission(request, "can_view", "/hr/sent-sms-list/"):
        return render(request, "403.html")

    all_params = dict(list(request.GET.items())[1:])
    query_string = urlencode(all_params)
    all_params["deleted"] = False
    page = request.GET.get("page", "")

    sent_sms_log_list = SMSLog.objects.filter(**all_params).order_by("-id")
    paginator = Paginator(sent_sms_log_list, 20)
    last_page_number = paginator.num_pages

    try:
        sent_sms_log_list = paginator.page(page)
    except PageNotAnInteger:
        sent_sms_log_list = paginator.page(1)
    except EmptyPage:
        sent_sms_log_list = paginator.page(paginator.num_pages)

    max_pages = 10
    current_page = sent_sms_log_list.number
    start_page = max(current_page - int(max_pages / 2), 1)
    end_page = start_page + max_pages
    if end_page > last_page_number:
        end_page = last_page_number + 1
        start_page = max(end_page - max_pages, 1)
    paginator_list = range(start_page, end_page)

    context = {
        "sent_sms_log_list": sent_sms_log_list,
        "last_page_number": last_page_number,
        "first_page_number": 1,
        "params": query_string,
        "all_params": all_params,
        "paginator_list": paginator_list,
    }
    return render(request, "crm/sent_sms_list.html", context)
# Settings
