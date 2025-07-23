import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from auditlog.registry import auditlog


class AdminUser(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    phone         = models.CharField(max_length=20, blank=True, null=True)
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    profile_image = models.ImageField(upload_to='admin_profile_images/', blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)

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
    user           = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    username       = models.CharField(max_length=100, blank=True, null=True)
    wrong_password = models.CharField(max_length=100, blank=True, null=True)
    login_ip       = models.CharField(max_length=100, blank=True, null=True)
    login_status   = models.BooleanField(default=False)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_logs"

    def __str__(self) -> str:
        return self.username


class BackendMenu(models.Model):
    module_name  = models.CharField(max_length=100, db_index=True)
    menu_name    = models.CharField(max_length=100, unique=True, db_index=True)
    menu_url     = models.CharField(max_length=250, unique=True)
    menu_icon    = models.CharField(max_length=250, blank=True, null=True)
    parent_id    = models.IntegerField()
    is_main_menu = models.BooleanField(default=False)
    is_sub_menu  = models.BooleanField(default=False)
    is_sub_child_menu = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = "backend_menu"

    def __str__(self) -> str:
        return self.menu_name


class UserMenuPermission(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_permission")
    menu       = models.ForeignKey(BackendMenu, on_delete=models.CASCADE, related_name="user_permission")
    can_view   = models.BooleanField(default=False)
    can_add    = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_by_user_permission")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="updated_by_user_permission", blank=True, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deleted_by_user_permission", blank=True, null=True)
    is_active  = models.BooleanField(default=True)
    deleted    = models.BooleanField(default=False)

    class Meta:
        db_table = "user_permission"

    def __str__(self):
        return str(self.menu)


# Frontend Settings
class FrontendSettings(models.Model):
    site_title    = models.CharField(max_length=255, default="My Website")
    logo          = models.ImageField(upload_to='settings/logo/', blank=True, null=True)
    favicon       = models.ImageField(upload_to='settings/favicon/', blank=True, null=True)

    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address       = models.TextField(blank=True, null=True)

    facebook_url  = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)

    created_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='frontend_settings_created_by')
    updated_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='frontend_settings_updated_by', blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        db_table = 'frontend_settings'
        verbose_name_plural = 'Frontend Settings'
        ordering = ['-is_active']

    def __str__(self):
        return self.site_title if self.site_title else "Frontend Settings"


class FrontendHeaderFooter(models.Model):
    title = models.CharField(max_length=255, default="My Website")
    image = models.ImageField(upload_to='settings/header/', blank=True, null=True)
    path = models.CharField(max_length=255, default="")
    type = models.CharField(max_length=50, choices=(('header', 'Header'), ('footer', 'Footer')), default='header')

    class Meta:
        db_table = 'frontend_header_footer'
        verbose_name_plural = 'Frontend Header & Footer'

    def __str__(self):
        return self.title if self.title else ""
    

class FrontendDesignSettings(models.Model):
    font_choices = (('arial', 'Arial'), ('verdana', 'Verdana'), ('times', 'Times New Roman'))

    header = models.ForeignKey(FrontendHeaderFooter, on_delete=models.CASCADE, related_name='header_design', blank=True, null=True)
    footer = models.ForeignKey(FrontendHeaderFooter, on_delete=models.CASCADE, related_name='footer_design', blank=True, null=True)
    primary_color = models.CharField(max_length=20, default="#000000")
    secondary_color = models.CharField(max_length=20, default="#FFFFFF")
    font_family = models.CharField(max_length=50, choices=font_choices, default='arial')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_settings_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_settings_updated_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)


class EmailConfiguration(models.Model):
    email_host      = models.CharField(max_length=255)
    email_port      = models.IntegerField()
    email_host_user = models.EmailField()
    email_host_password = models.CharField(max_length=255)
    use_tls        = models.BooleanField(default=True)
    use_ssl        = models.BooleanField(default=False)
    email_from_name = models.CharField(max_length=255, default="")
    created_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_config_created_by')
    updated_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_config_updated_by', blank=True, null=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'email_configuration'

    def __str__(self):
        return self.email_host_user


class SMSConfiguration(models.Model):
    sms_provider_choices = (('ssl', 'SSL'),)
    sms_configuration_type_choices = (('api_token', 'API Token'), ('password', 'Password'),)

    sms_provider = models.CharField(max_length=50, choices=sms_provider_choices, default='ssl', db_index=True)
    sms_configuration_type = models.CharField(max_length=100, choices=sms_configuration_type_choices, default='api_token', db_index=True)
    api_url      = models.URLField(max_length=255, blank=True, null=True)
    sms_id       = models.CharField(max_length=100, blank=True, null=True)
    api_token    = models.TextField(blank=True, null=True)
    username     = models.CharField(max_length=255, blank=True, null=True)
    password     = models.CharField(max_length=255, blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sms_config_created_by_user")
    updated_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sms_config_updated_by_user", blank=True, null=True)
    deleted_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sms_config_deleted_by_user", blank=True, null=True)
    status       = models.BooleanField(default=False)

    class Meta:
        db_table = "sms_configurations"

    def __str__(self):
        return f"{self.get_sms_provider_display()} - {self.get_sms_configuration_type_display()} ({self.sms_id})"


class SMSLog(models.Model):
    mobile_number = models.CharField(max_length=15, db_index=True)
    message_text  = models.TextField(blank=True, null=True)
    status        = models.CharField(max_length=15, blank=True, null=True)
    ip_address    = models.CharField(max_length=50, blank=True, null=True)
    sms_configuration = models.ForeignKey(SMSConfiguration, on_delete=models.CASCADE, blank=True, null=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    created_by    = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="sms_sent_created_by_user",
        blank=True, null=True
    )
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "sms_log"

    def __str__(self):
        return str(self.mobile_number)
# Frontend Settings


# Inventory
class ProductBrand(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(max_length=150, unique=True, blank=True)
    image       = models.ImageField(upload_to='inventory/brand_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ordering    = models.IntegerField(default=0)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brand_created_by')
    updated_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='brand_updated_by', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_brand'
        verbose_name_plural = 'Product Brands'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while ProductBrand.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductMainCategory(models.Model):
    name        = models.CharField(max_length=150, unique=True)
    slug        = models.SlugField(max_length=150, unique=True, blank=True)
    image       = models.ImageField(upload_to='ecommerce/category_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ordering    = models.IntegerField(default=0)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_created_by')
    updated_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_updated_by', blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_category'
        verbose_name_plural = 'Product Categories'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while ProductMainCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductSubCategory(models.Model):
    main_category  = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE)
    name           = models.CharField(max_length=150)
    slug           = models.SlugField(max_length=150, unique=True)
    image          = models.ImageField(upload_to='ecommerce/sub_category_images/', blank=True, null=True)
    description    = models.TextField(blank=True, null=True)
    ordering       = models.IntegerField(default=0)
    created_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_category_created_by')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_by     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sub_category_updated_by', blank=True, null=True)
    updated_at     = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_sub_category'
        verbose_name_plural = 'Product Sub Categories'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while ProductSubCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductChildCategory(models.Model):
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    name         = models.CharField(max_length=150)
    slug         = models.SlugField(max_length=150, unique=True)
    image        = models.ImageField(upload_to='ecommerce/child_category_images/', blank=True, null=True)
    description  = models.TextField(blank=True, null=True)
    ordering     = models.IntegerField(default=0)
    created_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_category_created_by')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_by   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='child_category_updated_by', blank=True, null=True)
    updated_at   = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active    = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while ProductChildCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'product_child_category'
        verbose_name_plural = 'Product Child Categories'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.name


class AttributeList(models.Model):
    name       = models.CharField(max_length=50, unique=True)
    ordering   = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_created_by')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attribute_updated_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        db_table = 'attribute_list'
        verbose_name_plural = 'Attribute List'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.name


class AttributeValueList(models.Model):
    attribute  = models.ForeignKey(AttributeList, on_delete=models.CASCADE)
    value      = models.CharField(max_length=50, unique=True)
    ordering   = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='value_created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='value_updated_by', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        db_table = 'value_list'
        verbose_name_plural = 'Attribute Value List'
        ordering = ['-is_active', 'ordering']

    def __str__(self):
        return self.value


class ProductList(models.Model):
    product_name = models.CharField(max_length=150)
    product_slug = models.SlugField(max_length=150, unique=True)
    product_sku = models.CharField(max_length=50, unique=True)
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, related_name='products')
    main_category = models.ForeignKey(ProductMainCategory, on_delete=models.CASCADE, related_name='products')
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    child_category = models.ForeignKey(ProductChildCategory, on_delete=models.DO_NOTHING, related_name='products', blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    product_image = models.ImageField(upload_to='ecommerce/product_images/', blank=True, null=True)
    product_home_image = models.ImageField(upload_to='ecommerce/product_home_images/', blank=True, null=True)
    product_video = models.FileField(upload_to='ecommerce/product_videos/', blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_status = models.BooleanField(default=False)
    discount_percent = models.IntegerField(default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_qty = models.IntegerField(default=0)
    sold_qty = models.IntegerField(default=0)
    return_qty = models.IntegerField(default=0)
    available_qty = models.IntegerField(default=0)
    STOCK_STATUS_CHOICES = (
        ('In Stock', 'In Stock'),
        ('Stock Out', 'Stock Out'),
    )
    stock_status = models.CharField(max_length=50, choices=STOCK_STATUS_CHOICES, default='In Stock')
    product_ordering = models.IntegerField(default=0)
    total_views = models.IntegerField(default=0)
    is_new_product = models.BooleanField(default=False)
    is_featured_product = models.BooleanField(default=False)
    is_combo_product = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_updated_by', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.product_slug and self.product_name:
            base_slug = slugify(self.product_name)
            slug = base_slug
            num = 1
            while ProductList.objects.filter(product_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.product_slug = slug

        if not self.product_sku:
            self.product_sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'products'
        verbose_name_plural = 'Products'
        ordering = ['-is_active', 'product_ordering']

    def __str__(self):
        return self.product_name


class ProductAttribute(models.Model):
    product    = models.ForeignKey(ProductList, on_delete=models.CASCADE)
    attribute  = models.ForeignKey(AttributeList, on_delete=models.CASCADE)
    value      = models.ForeignKey(AttributeValueList, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_attribute_created_by')
    updated_at = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_attribute_updated_by', blank=True, null=True)
    is_active  = models.BooleanField(default=True)

    class Meta:
        db_table = 'product_attribute'
        verbose_name_plural = 'Product Attributes'
        ordering = ['-is_active', 'created_at']

    def __str__(self):
        return str(self.product.product_name)


auditlog.register(AdminUser)
auditlog.register(LoginLog)
auditlog.register(BackendMenu)
auditlog.register(UserMenuPermission)
auditlog.register(FrontendSettings)
auditlog.register(EmailConfiguration)
auditlog.register(SMSConfiguration)
auditlog.register(SMSLog)
auditlog.register(ProductBrand)
auditlog.register(ProductMainCategory)
auditlog.register(ProductSubCategory)
auditlog.register(ProductChildCategory)
auditlog.register(AttributeList)
auditlog.register(AttributeValueList)
auditlog.register(ProductList)
auditlog.register(ProductAttribute)
