from django import forms
from django.contrib.auth.models import User

from .models import AdminUser, FrontendSettings, EmailConfiguration, SMSConfiguration

from .models import (
    ProductMainCategory, ProductSubCategory, ProductChildCategory, AttributeList, AttributeValueList, ProductList, ProductAttribute
)


class CustomUserLoginForm(forms.Form):
    """
    Custom form for user login.
    This form is used to authenticate users in the backend.
    """
    username = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        max_length=128, required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username.strip() if username else username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return password


class FrontendSettingsForm(forms.ModelForm):
    class Meta:
        model = FrontendSettings
        exclude = ['created_by', 'updated_by', 'created_at', 'updated_at', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'custom-file-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class EmailConfigurationForm(forms.ModelForm):
    class Meta:
        model = EmailConfiguration
        fields = [
            'email_host', 'email_port', 'email_host_user', 'email_host_password', 'use_tls', 'use_ssl',
        ]
        widgets = {
            'email_host': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email_port': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email_host_user': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email_host_password': forms.PasswordInput(attrs={'class': 'form-control', 'required': 'required'}),
            'use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        read_only = kwargs.pop('read_only', False)
        super().__init__(*args, **kwargs)
        if read_only:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True
        else:
            self.fields['email_host'].empty_label = ""


class SMSConfigurationForm(forms.ModelForm):
    class Meta:
        model = SMSConfiguration
        fields = [
            'sms_provider', 'sms_configuration_type', 'api_url', 'sms_id', 'api_token', 'username', 'password',
        ]
        widgets = {
            'sms_provider': forms.Select(attrs={'class': 'form-control select2_items', 'required': 'required'}),
            'sms_configuration_type': forms.Select(attrs={'class': 'form-control select2_items', 'required': 'required', 'id': 'id_sms_configuration_type'}),
            'api_url': forms.TextInput(attrs={'class': 'form-control'}),
            'sms_id': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'api_token': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        read_only = kwargs.pop('read_only', False)
        super().__init__(*args, **kwargs)
        if read_only:
            for field in self.fields.values():
                field.widget.attrs['readonly'] = True
                field.widget.attrs['disabled'] = True
        else:
            self.fields['sms_provider'].empty_label = ""


class UserCreateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100, required=False)
    email = forms.EmailField()
    date_of_birth = forms.DateField(required=False)

    class Meta:
        model = AdminUser
        fields = ['phone', 'gender', 'profile_image']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.user.pk if self.instance and hasattr(self.instance, 'user') else None
        if User.objects.exclude(pk=user_id).filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email

    def save(self, commit=True):
        admin_user = super().save(commit=False)

        if self.instance and hasattr(self.instance, 'user'):
            user = self.instance.user
        else:
            user = User()

        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email')
        user.username = user.email

        user.set_password('12345678')

        if commit:
            user.save()
            admin_user.user = user
            admin_user.save()

        return admin_user


class ProductMainCategoryForm(forms.ModelForm):

    class Meta:
        model = ProductMainCategory
        fields = ['main_cat_name', 'cat_image', 'description', 'cat_ordering']

        widgets = {
            'main_cat_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'cat_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cat_ordering': forms.NumberInput(attrs={'class': 'form-control'})
        }


class ProductSubCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductSubCategory
        fields = ['main_category', 'sub_cat_name', 'sub_cat_image', 'description', 'sub_cat_ordering']

        widgets = {
            'main_category': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'sub_cat_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'sub_cat_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'sub_cat_ordering': forms.NumberInput(attrs={'class': 'form-control'})
        }


class ProductChildCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductChildCategory
        fields = ['sub_category', 'child_cat_name', 'child_cat_image', 'description', 'child_cat_ordering']

        widgets = {
            'sub_category': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'child_cat_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'child_cat_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'child_cat_ordering': forms.NumberInput(attrs={'class': 'form-control'})
        }


class AttributeListForm(forms.ModelForm):
    class Meta:
        model = AttributeList
        fields = ['attribute_name', 'attribute_ordering']

        widgets = {
            'attribute_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'attribute_ordering': forms.NumberInput(attrs={'class': 'form-control'})
        }


class AttributeValueListForm(forms.ModelForm):
    class Meta:
        model = AttributeValueList
        fields = ['attribute', 'attribute_value', 'attribute_value_ordering']
        
        widgets = {
            'attribute': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'attribute_value': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'attribute_value_ordering': forms.NumberInput(attrs={'class': 'form-control'})
        }


class ProductListForm(forms.ModelForm):
    class Meta:
        model = ProductList
        exclude = ['product_slug', 'product_sku', 'available_qty', 'new_product', 'created_by', 'updated_by', 'updated_at', 'created_at', 'is_active', 'sold_qty', 'return_qty', 'total_views']

        widgets = {
            'main_category': forms.Select(attrs={'class': 'form-control select2-single', 'required': True}),
            'sub_category': forms.Select(attrs={'class': 'form-control select2-single'}),
            'child_category': forms.Select(attrs={'class': 'form-control select2-single'}),
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'product_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'guideline': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'sale_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'total_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'sold_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'return_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_status': forms.Select(attrs={'class': 'form-control select2-single'}),
            'product_ordering': forms.NumberInput(attrs={'class': 'form-control'}),
            'warranty': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'variant_product': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # 'template_product': forms.Select(attrs={'class': 'form-control'}),
            'is_combo_product': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['product', 'attribute', 'attribute_value']

        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'attribute': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'attribute_value': forms.Select(attrs={'class': 'form-control', 'required': True}),
        }
