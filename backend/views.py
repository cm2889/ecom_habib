from django.db.models import Q 
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
class ProductBrandListView(ListView):
    model          = ProductBrand
    template_name  = 'product/brand/brand_list.html' 
    paginated_by   = None 

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_view', 'backend/brand-list'):
            return render(request, '403.html') 
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return ProductBrand.objects.filter(is_active=True).order_by('-id')
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num   = self.request.GET.get('page', 1)
        full_query = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_query)

        context.update({
            'brand_list' : paginated_data,
            'page_num'   : page_num,
            'paginator_list' : paginator_list, 
            'last_page_number' : last_page_number
        })

        return context 


@login_required
def product_brand_detail_view(request, pk):
    if not checkUserPermission(request, 'can_view', 'backend/brand-list'):
        messages.error(request, 'You have not permission to view')
        return render(request, '403.html')

    brand = get_object_or_404(ProductBrand, pk=pk)
    context = {
        'brand': brand
    }
    return render(request, 'product/brand/brand_detail.html', context)



@method_decorator(login_required, name='dispatch')
class ProductBrandCreateView(CreateView):
    model          = ProductBrand 
    form_class     = ProductBrandForm 
    template_name  = 'product/brand/add_brand.html' 
    success_url    = reverse_lazy('backend:product_brand_list')
 

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_add', 'backend/brand-list'):
            messages.error(request, 'You have not permision to add brand ')
            return render(request, '403.html') 
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductBrandUpdateView(UpdateView):
    model         = ProductBrand
    form_class    = ProductBrandForm
    template_name = 'product/brand/update_brand.html'
    success_url   = reverse_lazy('backend:product_brand_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, 'can_update', 'backend/brand-list'):
            messages.error(request, 'You do not have permission to update this brand.')
            return render(request, '403.html')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Brand updated successfully.')
        return super().form_valid(form)


@login_required
def product_brand_delete_view(request, pk):
    if not checkUserPermission(request, 'can_delete', 'backend/brand-list'):
        return render(request, '403.html')
    
    brand = get_object_or_404(ProductBrand, pk=pk)

    if request.method == 'POST':
        brand.is_active = False 
        brand.save()
        messages.success(request, 'Product brand deleted successfully!')
        return redirect('backend:product_brand_list')

    return redirect('backend:product_brand_list')


@method_decorator(login_required, name='dispatch')
class ProductMainCategoryListView(ListView):
    model = ProductMainCategory
    template_name = 'product/maincategories/main_cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/main_cat_list/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ProductMainCategory.objects.filter(is_active=True).order_by('-id')

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

        return context
    

@login_required
def product_main_category_datails_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/product-main-category-details/"):
        messages.error(request, "You do not have permission to view this product main category.")
        return render(request, "403.html")

    main_category_details = get_object_or_404(ProductMainCategory, pk=pk)
    
    context = {
        'main_category_details': main_category_details
    }
    return render(request, 'product/maincategories/cat_details.html', context)


@method_decorator(login_required, name='dispatch')
class ProductMainCategoryCreateView(CreateView):
    model = ProductMainCategory
    form_class = ProductMainCategoryForm
    template_name = 'product/maincategories/add_category.html'
    success_url = reverse_lazy('backend:product_main_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/add-product-main-category/"):
            messages.error(request, "You do not have permission to add a product main category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product main category created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductMainCategoryUpdateView(UpdateView):
    model = ProductMainCategory
    form_class = ProductMainCategoryForm
    template_name = 'product/maincategories/update_category.html'
    success_url = reverse_lazy('backend:product_main_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_update", "backend/product-main-category-update/"):
            messages.error(request, "You do not have permission to update this product main category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product main category updated successfully.")
        return super().form_valid(form)
    

@login_required
def product_main_category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/product-main-category-delete/"):
        return render(request, "403.html")

    category = get_object_or_404(ProductMainCategory, pk=pk)

    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, "Product main category deleted successfully.")
        return redirect('backend:product_main_category_list')

    return redirect('backend:product_main_category_list')


@method_decorator(login_required, name='dispatch')
class ProductSubCategoryListView(ListView):
    model = ProductSubCategory
    template_name = 'product/subcategories/cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/product-main-category-list/"):
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
def product_sub_category_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/product-main-category-list/"):
        messages.error(request, "You do not have permission to view this product sub category.")
        return render(request, "403.html")

    sub_category_details = get_object_or_404(ProductSubCategory, pk=pk)

    context = {
        'sub_category_details': sub_category_details
    }
    return render(request, 'product/subcategories/cat_details.html', context)


@method_decorator(login_required, name='dispatch')
class ProductSubCategoryCreateView(CreateView):
    model = ProductSubCategory
    form_class = ProductSubCategoryForm
    template_name = 'product/subcategories/add_category.html'
    success_url = reverse_lazy('backend:product_sub_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/product-main-category-list/"):
            messages.error(request, "You do not have permission to add a product sub category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product sub category created successfully.")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProductSubCategoryUpdateView(UpdateView):
    model = ProductSubCategory
    form_class = ProductSubCategoryForm
    template_name = 'product/subcategories/cat_update.html'
    success_url = reverse_lazy('backend:product_sub_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_update", "backend/product-main-category-list/"):
            messages.error(request, "You do not have permission to update this product sub category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product sub category updated successfully.")
        return super().form_valid(form)
    

@login_required
def product_sub_category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/product-sub-category-delete/"):
        return render(request, "403.html")

    sub_category = get_object_or_404(ProductSubCategory, pk=pk)

    if request.method == 'POST':
        sub_category.is_active = False
        sub_category.save()
        messages.success(request, "Product sub category deleted successfully.")
        return redirect('backend:product_sub_category_list')

    return redirect('backend:product_sub_category_list')


class ProductChildCategoryListView(ListView):
    model = ProductChildCategory
    template_name = 'product/childcategories/cat_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/product-child-category-list/"):
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
def product_child_category_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/product-child-category-details/"):
        messages.error(request, "You do not have permission to view this product child category.")
        return render(request, "403.html")

    child_category_details = get_object_or_404(ProductChildCategory, pk=pk)

    context = {
        'child_category_details': child_category_details
    }
    return render(request, 'product/childcategories/cat_details.html', context)


class ProductChildCategoryCreateView(CreateView):
    model = ProductChildCategory
    form_class = ProductChildCategoryForm
    template_name = 'product/childcategories/add_category.html'
    success_url = reverse_lazy('backend:product_child_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_add", "backend/product-child-category-list/"):
            messages.error(request, "You do not have permission to add a product child category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Product child category created successfully.")
        return super().form_valid(form)


class ProductChildCategoryUpdateView(UpdateView):
    model = ProductChildCategory
    form_class = ProductChildCategoryForm
    template_name = 'product/childcategories/cat_update.html'
    success_url = reverse_lazy('backend:product_child_category_list')

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_edit", "backend/product-child-category-list/"):
            messages.error(request, "You do not have permission to update this product child category.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product child category updated successfully.")
        return super().form_valid(form)


@login_required
def product_child_category_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/product-child-category-delete/"):
        return render(request, "403.html")

    child_category = get_object_or_404(ProductChildCategory, pk=pk)

    if request.method == 'POST':
        child_category.is_active = False
        child_category.save()
        messages.success(request, "Product child category deleted successfully.")
        return redirect('backend:product_child_category_list')

    return redirect('backend:product_child_category_list')


@method_decorator(login_required, name='dispatch')
class AttributeListView(ListView):
    model = AttributeList
    template_name = 'product/attributes/attribute_list.html'
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/attribute-list/"):
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
    if not checkUserPermission(request, "can_view", "backend/attribute-details/"):
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
        if not checkUserPermission(request, "can_add", "backend/attribute-list/"):
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
        if not checkUserPermission(request, "can_edit", "backend/attribute-list/"):
            messages.error(request, "You do not have permission to update this attribute.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Attribute updated successfully.")
        return super().form_valid(form)


@login_required
def attribute_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/attribute-delete/"):
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
    paginate_by = None

    def dispatch(self, request, *args, **kwargs):
        if not checkUserPermission(request, "can_view", "backend/product-list/"):
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        filters = {'is_active' : True}

        name        = self.request.GET.get('name') 
        category_id = self.request.GET.get('category')
        brand       = self.request.GET.get('brand')
        created_from = self.request.GET.get('created_from')
        created_to   = self.request.GET.get('created_to') 

        if created_from:
            filters['created_at__gte'] = created_from
        if created_to:
            filters['created_at__lte'] = created_to 

        if name:
            filters['product_name__icontains'] = name
        if category_id:
            filters['main_category__id'] = category_id
        if brand:
            filters['brand__id'] = brand
        
        return ProductList.objects.filter(**filters).order_by('-id')
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_num = self.request.GET.get('page', 1)
        full_queryset = self.get_queryset()

        paginated_data, paginator_list, last_page_number = paginate_data(self.request, page_num, full_queryset)

        context.update({
            'products': paginated_data,
            'page_num': page_num,
            'paginator_list': paginator_list,
            'last_page_number': last_page_number,

            'filter_created_from': self.request.GET.get('created_from', ''),
            'filter_created_to': self.request.GET.get('created_to', ''),
            'filter_name': self.request.GET.get('name', ''),
            'filter_category': self.request.GET.get('category', ''),
            'filter_brand': self.request.GET.get('brand', ''),
            'categories'  : ProductMainCategory.objects.filter(is_active=True).order_by('name'),
            'brands'      : ProductBrand.objects.filter(is_active=True).order_by('name'),


        })
        
        return context


@login_required
def product_details_view(request, pk):
    if not checkUserPermission(request, "can_view", "backend/product-details/"):
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
        if not checkUserPermission(request, "can_add", "backend/product-list/"):
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
        if not checkUserPermission(request, "can_edit", "backend/product-list/"):
            messages.error(request, "You do not have permission to update this product.")
            return render(request, "403.html")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, "Product updated successfully.")
        return super().form_valid(form)
    

@login_required
def product_delete_view(request, pk):
    if not checkUserPermission(request, "can_delete", "backend/product-delete/"):
        return render(request, "403.html")

    product = get_object_or_404(ProductList, pk=pk)

    if request.method == 'POST':
        product.is_active = False
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
#         name = request.POST.get('name').strip()
#         description   = request.POST.get('description').strip()
#         ordering  = request.POST.get('ordering').strip()
#         image     = request.FILES.get('image')

#         if not name:
#             messages.error(request, "Name is required.")
#             return redirect('add_product_main_category')

#         ProductMainCategory.objects.create(
#             name=name,
#             description=description,
#             ordering=ordering,
#             image=image,
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

#     opt_main_category  = ProductMainCategory.objects.filter(is_active=True).values('id', 'name').order_by('-id')

#     if request.method == "POST":
#         main_category       = request.POST.get('main_category').strip()
#         name        = request.POST.get('name').strip()
#         slug        = request.POST.get('slug').strip()
#         description         = request.POST.get('description').strip()
#         image       = request.FILES.get('image')
#         ordering    = request.POST.get('ordering').strip()

#         if not main_category or not name:
#             messages.error(request, 'Name is required')
#             return redirect('add_product_sub_category')
        
#         try:
#             main_category_obj = ProductMainCategory.objects.get(id=main_category)
#             ProductSubCategory.objects.create(
#                 main_category    = main_category_obj,
#                 name     = name,
#                 description      = description,
#                 image    = image,
#                 ordering = int(ordering) if ordering else 0,
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

#     opt_main_category = ProductMainCategory.objects.filter(is_active=True).values('id', 'name').order_by('-id')

#     if request.method  == "POST":
#         main_category       = request.POST.get('main_category').strip()
#         name        = request.POST.get('name').strip()
#         slug        = request.POST.get('slug').strip()
#         description         = request.POST.get('description').strip()
#         image       = request.FILES.get('image')
#         ordering    = request.POST.get('ordering').strip()
#         is_active           = request.POST.get('is_active') == 'on'

#         if not main_category or not name:
#             messages.error(request, 'Name is required')
#             return redirect('product_sub_category_update', pk=pk)
    
#         try:
#             main_category_obj = ProductMainCategory.objects.get(id=main_category)
#             category.main_category    = main_category_obj
#             category.name     = name
#             category.slug     = slug if slug else category.slug
#             category.description      = description
#             if image:
#                 category.image = image
#             category.ordering = int(ordering) if ordering else 0
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

#     opt_sub_category = ProductSubCategory.objects.filter(is_active=True).values('id', 'name').order_by('-id')

#     if request.method == "POST":
#         sub_cate_name       = request.POST.get('sub_cate_name').strip()
#         name      = request.POST.get('name').strip()
#         slug      = request.POST.get('slug').strip()
#         description         = request.POST.get('description').strip()
#         ordering  = request.POST.get('ordering').strip()
#         image     = request.FILES.get('image')

#         if not sub_cate_name or not name:
#             messages.error(request, 'Name is required')
#             return redirect('add_product_child_category')
        

#         try:
#             sub_category_obj   = ProductSubCategory.objects.get(id=sub_cate_name)
#             ProductChildCategory.objects.create(
#                 sub_category      = sub_category_obj,
#                 name    = name,
#                 description       = description,
#                 image   = image,
#                 ordering= int(ordering) if ordering else 0,
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

#     opt_sub_category = ProductSubCategory.objects.filter(is_active=True).values('id', 'name').order_by('-id')

#     if request.method == "POST":
#         sub_cate_name       = request.POST.get('sub_cate_name').strip()
#         name      = request.POST.get('name').strip()
#         slug      = request.POST.get('slug').strip()
#         description         = request.POST.get('description').strip()
#         image     = request.FILES.get('image')
#         ordering  = request.POST.get('ordering').strip()

#         if not sub_cate_name or not name:
#             messages.error(request, 'Name is required')
#             return redirect('product_child_category_update', pk=pk)
        
#         try:
#             sub_category_obj   = ProductSubCategory.objects.get(id=sub_cate_name)
#             category.sub_category      = sub_category_obj
#             category.name    = name
#             category.slug    = slug if slug else category.slug
#             category.description       = description
#             if image:
#                 category.image = image
#             category.ordering= int(ordering) if ordering else 0
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
# def value_list_view(request):
#     """
#     View to list all active attribute values.
#     This view checks user permissions and paginates the list of attribute values.
#     If the user does not have permission to view the list, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-value-list/"):
#         return redirect('dashboard')

#     values = AttributeValueList.objects.filter(is_active=True).order_by('-id')
#     page_number = request.GET.get('page', 1)
#     values, paginator_list, last_page_number = paginate_data(request, page_number, values)

#     context = {
#         'paginator_list': paginator_list,
#         'last_page_number': last_page_number,
#         'values': values,
#     }
#     return render(request, "product/value_list.html", context)


# @login_required
# def value_details_view(request, pk):
#     """
#     View to display the details of a specific attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to view the details, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_view", "backend/attribute-value-details/"):
#         return redirect('dashboard')
#     value = get_object_or_404(AttributeValueList, pk=pk)
#     context['value'] = value
#     return render(request, 'product/', context)


# @login_required
# def value_create_view(request):
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
#             return redirect('value_list')
#     else:
#         form = AttributeValueListForm()

#     context['form'] = form
    
#     return render(request, 'product/', context)


# @login_required
# def value_update_view(request, pk):
#     """
#     View to update an existing attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to update the attribute value, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_edit", "backend/edit-attribute-value/"):
#         return redirect('dashboard')
#     value = get_object_or_404(AttributeValueList, pk=pk)
#     if request.method == "POST":
#         form = AttributeValueListForm(request.POST, instance=value)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Attribute value updated successfully.")
#             return redirect('value_list')
#     else:
#         form = AttributeValueListForm(instance=value)

#     context['form'] = form
#     return render(request, 'product/', context)


# @login_required
# def value_delete_view(request, pk):
#     """
#     View to delete an attribute value.
#     This view checks user permissions and retrieves the attribute value by its primary key (pk).
#     If the user does not have permission to delete the attribute value, they are redirected to the dashboard.
#     """
#     context = {}
#     if not checkUserPermission(request, "can_delete", "backend/delete-attribute-value/"):
#         return redirect('dashboard')
#     value = get_object_or_404(AttributeValueList, pk=pk)
#     if request.method == "POST":
#         value.is_active = False
#         value.save()
#         messages.success(request, "Attribute value deleted successfully.")
#         return redirect('value_list')
    
#     context['value'] = value
#     return render(request, 'product/', context)


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
