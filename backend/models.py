from django.db import models
from django.contrib.auth.models import User
# from django.utils.text import slugify

from auditlog.registry import auditlog


class AdminUser(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    profile_image = models.ImageField(upload_to='admin_profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_user'

    def get_name(self):
        first_name = self.user.first_name.strip() if self.user.first_name else ""
        last_name = self.user.last_name.strip() if self.user.last_name else ""
        return f"{first_name} {last_name}".strip() if first_name or last_name else self.user.username

    def get_profile_photo_url(self):
        if self.profile_image:
            return self.profile_image.url
        return f"https://ui-avatars.com/api/?name={self.get_name()}&background=random"

    def __str__(self):
        return self.get_name() if self.user else ""


class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    wrong_password = models.CharField(max_length=100, blank=True, null=True)
    login_ip = models.CharField(max_length=100, blank=True, null=True)
    login_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_logs"

    def __str__(self) -> str:
        return self.username


class BackendMenu(models.Model):
    module_name = models.CharField(max_length=100, db_index=True)
    menu_name = models.CharField(max_length=100, unique=True, db_index=True)
    menu_url = models.CharField(max_length=250, unique=True)
    menu_icon = models.CharField(max_length=250, blank=True, null=True)
    parent_id = models.IntegerField()
    is_main_menu = models.BooleanField(default=False)
    is_sub_menu = models.BooleanField(default=False)
    is_sub_child_menu = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "backend_menu"

    def __str__(self) -> str:
        return self.menu_name


class UserMenuPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_permission")
    menu = models.ForeignKey(BackendMenu, on_delete=models.CASCADE, related_name="user_permission")
    can_view = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_user_permission")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="updated_by_user_permission", blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deleted_by_user_permission", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "user_permission"

    def __str__(self):
        return str(self.menu)


# class UserGroup(models.Model):
#     group_name     = models.CharField(max_length=100, unique=True, db_index=True) 
#     description    = models.CharField(max_length=250, blank=True, null=True) 
#     created_at     = models.DateTimeField(auto_now_add=True)
#     updated_at     = models.DateTimeField(blank=True, null=True)
#     created_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_group_created_by_user")
#     updated_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_group_updated_by_user", blank=True, null=True)
#     deleted_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_group_deleted_by_user", blank=True, null=True)
#     is_active      = models.BooleanField(default=True)
#     deleted        = models.BooleanField(default=False)

#     def __str__(self):
#         return str(self.group.group_name)

#     class Meta:
#         db_table = "user_groups"
        
# class GroupWiseMenu(models.Model):
#     user_group  = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='group_permissions')
#     menu        = models.ForeignKey(BackendMenu, on_delete=models.CASCADE, related_name='group_permissions')
#     can_view    = models.BooleanField(default=False)
#     can_add     = models.BooleanField(default=False)
#     can_update  = models.BooleanField(default=False)
#     can_delete  = models.BooleanField(default=False)
#     created_at  = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(blank=True, null=True)
#     created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_permission_created_by_user")
#     updated_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_permission_updated_by_user", blank=True, null=True) 
#     deleted_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_permission_deleted_by_user", blank=True, null=True)
#     is_active   = models.BooleanField(default=True)
#     deleted     = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user_group.group_name} > {self.menu.menu_name}"

#     class Meta:
#         db_table = "group_wise_menus"


# class City(models.Model):
#     name = models.CharField(max_length=100, unique=True, db_index=True)
#     state = models.CharField(max_length=100, blank=True, null=True)
#     country = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     deleted = models.BooleanField(default=False)

#     class Meta:
#         db_table = "city"

#     def __str__(self):
#         return self.name   
    
# class Industry(models.Model):
#     name = models.CharField(max_length=100, unique=True, db_index=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at  = models.DateTimeField(blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     deleted = models.BooleanField(default=False)

#     class Meta:
#         db_table = "industries"

#     def __str__(self):
#         return self.name 




# class Company(models.Model):
#     name = models.CharField(max_length=255)
#     logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
#     description = models.TextField(blank=True, null=True)

#     email = models.EmailField(blank=True, null=True)
#     phone = models.CharField(max_length=20, blank=True)
#     website = models.URLField(blank=True)

#     address = models.CharField(max_length=255, blank=True)
#     city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='companies')
#     industry = models.ForeignKey('Industry', on_delete=models.SET_NULL, null=True, blank=True, related_name='industies')
#     established_year = models.PositiveIntegerField(blank=True, null=True)
#     number_of_employees = models.PositiveIntegerField(blank=True, null=True)

#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name




# class EmployeeType(models.Model):
#     name = models.CharField(max_length=100, unique=True, db_index=True)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)
#     deleted = models.BooleanField(default=False)

#     class Meta:
#         db_table = "employee_type"

#     def __str__(self):
#         return self.name





# class Employee(models.Model):
    
#     first_name          = models.CharField(max_length=50)
#     last_name           = models.CharField(max_length=50, blank=True, null=True)
#     blood_group         = models.CharField(
#         max_length=3,
#         choices=(
#             ('A+', 'A+'), ('A-', 'A-'),
#             ('B+', 'B+'), ('B-', 'B-'),
#             ('AB+', 'AB+'), ('AB-', 'AB-'),
#             ('O+', 'O+'), ('O-', 'O-'),
#         ),
#         blank=True, null=True
#     )
#     employee_image        = models.ImageField(upload_to='doctor_images/', blank=True, null=True)
#     employee_id_number    = models.CharField(max_length=20, unique=True, db_index=True)
#     fathers_name        = models.CharField(max_length=50, blank=True, null=True)
#     mothers_name        = models.CharField(max_length=50, blank=True, null=True)
#     user                = models.OneToOneField(User, on_delete=models.DO_NOTHING, blank=True, null=True)
#     date_of_birth       = models.DateField(blank=True, null=True)
#     gender              = models.CharField(
#         max_length=6,
#         choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')),
#         blank=True, null=True
#     )
#     religion            = models.CharField(
#         max_length=9,
#         choices=(
#             ('Islam', 'Islam'),
#             ('Hindu', 'Hindu'),
#             ('Christian', 'Christian'),
#             ('Buddha', 'Buddha'),
#             ('Others', 'Others')
#         ),
#         blank=True, null=True
#     )
#     marital_status      = models.CharField(
#         max_length=10,
#         choices=(
#             ('Unmarried', 'Unmarried'),
#             ('Married', 'Married'),
#             ('Widowed', 'Widowed'),
#             ('Divorced', 'Divorced')
#         ),
#         blank=True, null=True
#     )
#     contact_number      = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)
#     email               = models.EmailField(max_length=100, blank=True, null=True)
#     address             = models.TextField(blank=True, null=True)
#     city                = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
#     receive_online_notifiation = models.BooleanField(default=False)
#     created_at          = models.DateTimeField(auto_now_add=True)
#     updated_at          = models.DateTimeField(auto_now=True)
#     is_department_head = models.BooleanField(default=False, help_text="Indicates if the doctor is a department head")
#     employee_type         = models.ForeignKey(EmployeeType, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
#     deleted_at          = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     created_by          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_created_by_users', blank=True, null=True)
#     updated_by          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_updated_by_users', blank=True, null=True)
#     deleted_by          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_deleted_by_users', blank=True, null=True)
#     is_active           = models.BooleanField(default=True)
#     deleted             = models.BooleanField(default=False)
    

    
#     class Meta:
#         db_table = "employee"

#     def __str__(self):
#         return str(self.first_name.strip() if self.first_name else "") + ' ' + str(self.last_name.strip() if self.last_name else "")  




# class ProductMainCategory(models.Model):
#     main_cat_name = models.CharField(max_length=100, unique=True)
#     cat_slug      = models.SlugField(max_length=150, unique=True, blank=True)
#     cat_image     = models.ImageField(upload_to='ecommerce/category_images/', blank=True, null=True)
#     description   = models.TextField(blank=True, null=True)
#     cat_ordering  = models.IntegerField(default=0)
#     created_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_created_by')
#     updated_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_updated_by', blank=True, null=True)
#     created_at    = models.DateTimeField(auto_now_add=True)
#     updated_at    = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active     = models.BooleanField(default=True)

#     class Meta:
#         db_table = 'product_category'
#         verbose_name_plural = 'Product Categories'
#         ordering = ['-is_active','cat_ordering']

#     def __str__(self):
#         return self.main_cat_name

#     def save(self, *args, **kwargs):
#         if not self.cat_slug and self.main_cat_name:
#             base_slug = slugify(self.main_cat_name)
#             slug = base_slug
#             num = 1
#             while ProductMainCategory.objects.filter(cat_slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base_slug}-{num}"
#                 num += 1
#             self.cat_slug = slug
#         super().save(*args, **kwargs)





# class ProductSubCategory(models.Model):
#     main_category    = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE)
#     sub_cat_name     = models.CharField(max_length=150)
#     sub_cat_slug     = models.SlugField(max_length=150, unique=True)
#     sub_cat_image    = models.ImageField(upload_to='ecommerce/sub_category_images/', blank=True, null=True)
#     description      = models.TextField(blank=True, null=True)
#     sub_cat_ordering = models.IntegerField(default=0)
#     created_by       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_category_created_by')
#     created_at       = models.DateTimeField(auto_now_add=True)
#     updated_by       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_category_updated_by', blank=True, null=True)
#     updated_at       = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active        = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'product_sub_category'
#         verbose_name_plural = 'Product Sub Categories'
#         ordering = ['-is_active','sub_cat_ordering']

#     def __str__(self):
#         return self.sub_cat_name
    
#     def save(self, *args, **kwargs):
#         if not self.sub_cat_slug and self.sub_cat_name:
#             base_slug = slugify(self.sub_cat_name)
#             slug = base_slug
#             num = 1
#             while ProductSubCategory.objects.filter(sub_cat_slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base_slug}-{num}"
#                 num += 1
#             self.sub_cat_slug = slug
#         super().save(*args, **kwargs)
    



    
# class ProductChildCategory(models.Model):
#     sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
#     child_cat_name = models.CharField(max_length=150)
#     child_cat_slug = models.SlugField(max_length=150, unique=True)
#     child_cat_image = models.ImageField(upload_to='ecommerce/child_category_images/', blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     child_cat_ordering = models.IntegerField(default=0)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_category_created_by')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_category_updated_by', blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active = models.BooleanField(default=True)


#     def save(self, *args, **kwargs):
#         if not self.child_cat_slug and self.child_cat_name:
#             base_slug = slugify(self.child_cat_name)
#             slug = base_slug
#             num = 1
#             while ProductChildCategory.objects.filter(child_cat_slug=slug).exclude(pk=self.pk).exists():
#                 slug = f"{base_slug}-{num}"
#                 num += 1
#             self.child_cat_slug = slug
#         super().save(*args, **kwargs)

#     class Meta:
#         db_table = 'product_child_category'
#         verbose_name_plural = 'Product Child Categories' 
#         ordering = ['-is_active','child_cat_ordering']

#     def __str__(self):
#         return self.child_cat_name




# class AttributeList(models.Model):
#     attribute_name = models.CharField(max_length=50, unique=True)
#     attribute_ordering = models.IntegerField(default=0)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_created_by')
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_updated_by', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'attribute_list'
#         verbose_name_plural = 'Attribute List' 
#         ordering = ['-is_active','attribute_ordering']

#     def __str__(self):
#         return self.attribute_name
    



# class AttributeValueList(models.Model):
#     attribute = models.ForeignKey(AttributeList, on_delete=models.CASCADE)
#     attribute_value = models.CharField(max_length=50, unique=True)
#     attribute_value_ordering = models.IntegerField(default=0)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_value_created_by')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_value_updated_by', blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'attribute_value_list'
#         verbose_name_plural = 'Attribute Value List' 
#         ordering = ['-is_active','attribute_value_ordering']

#     def __str__(self):
#         return self.attribute_value
    


# class ProductList(models.Model):
#     product_name = models.CharField(max_length=150)
#     product_slug = models.SlugField(max_length=150, unique=True)
#     product_sku = models.CharField(max_length=50, unique=True)
#     main_category = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE)
#     sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, blank=True, null=True)
#     child_category = models.ForeignKey(ProductChildCategory, on_delete=models.DO_NOTHING, blank=True, null=True) 
#     description = models.TextField(blank=True, null=True)
#     guideline = models.TextField(blank=True, null=True)
#     product_image = models.ImageField(upload_to='ecommerce/product_images/', blank=True, null=True)
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
#     discount_percent = models.IntegerField(default=0)
#     discount_status = models.BooleanField(default=False)
#     total_qty = models.IntegerField(default=0)
#     sold_qty = models.IntegerField(default=0)
#     return_qty = models.IntegerField(default=0)
#     available_qty = models.IntegerField(default=0)
#     STOCK_STATUS_CHOICES = (
#         ('In Stock', 'In Stock'),
#         ('Out of Stock', 'Out of Stock'),
#         ('Upcoming', 'Upcoming'),
#         ('Discontinue', 'Discontinue'),
#     )
#     stock_status = models.CharField(max_length=50, choices=STOCK_STATUS_CHOICES, default='In Stock')
#     product_ordering = models.IntegerField(default=0)
#     total_views = models.IntegerField(default=0)
#     new_product = models.IntegerField(default=0)
#     warranty = models.BooleanField(default=False)
#     variant_product = models.BooleanField(default=False)
#     template_product = models.ForeignKey('self', on_delete=models.CASCADE, related_name='product_template', blank=True, null=True)
#     is_combo_product = models.BooleanField(default=False)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_created_by')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_updated_by', blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'products'
#         verbose_name_plural = 'Products'
#         ordering = ['-is_active','product_ordering']

#     def __str__(self):
#         return self.product_name
    


# class ProductAttribute(models.Model):
#     product         = models.ForeignKey(ProductList, on_delete=models.CASCADE)
#     attribute       = models.ForeignKey(AttributeList, on_delete=models.CASCADE)
#     attribute_value = models.ForeignKey(AttributeValueList, on_delete=models.CASCADE)
#     created_at      = models.DateTimeField(auto_now_add=True)
#     created_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_attribute_created_by')
#     updated_at      = models.DateTimeField(auto_now_add=False, blank=True, null=True)
#     updated_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_attribute_updated_by', blank=True, null=True)
#     is_active       = models.BooleanField(default=True)
    
#     class Meta:
#         db_table = 'product_attribute'
#         verbose_name_plural = 'Product Attributes'
#         ordering = ['-is_active','created_at']

#     def __str__(self):
#         return str(self.product.product_name)


auditlog.register(AdminUser)
auditlog.register(LoginLog)
auditlog.register(BackendMenu)
auditlog.register(UserMenuPermission)
