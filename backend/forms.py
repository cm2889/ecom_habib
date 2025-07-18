from django import forms
from django.contrib.auth.models import User

from .models import AdminUser, FrontendSettings, EmailConfiguration, SMSConfiguration

# from .models import ProductMainCategory, ProductSubCategory, ProductChildCategory, AttributeList, AttributeValueList


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


# class ProductMainCategoryForm(forms.ModelForm):
#     """
#     Form for Product Main Category
#     This form is used to create or update ProductMainCategory instances.
#     It includes all fields from the ProductMainCategory model.
#     """
    
#     created = forms.DateTimeField(required=False, widget=forms.HiddenInput())
#     updated = forms.DateTimeField(required=False, widget=forms.HiddenInput())

#     class Meta:
#         model = ProductMainCategory
#         fields = ['main_cat_name', 'cat_slug', 'cat_image', 'description', 'cat_ordering', 'is_active', 'created', 'updated']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             # For new instances, remove created and updated fields
#             self.fields.pop('created')
#             self.fields.pop('updated')


# class ProductSubCategoryForm(forms.ModelForm):
#     """   Form for Product Sub Category
#     This form is used to create or update ProductSubCategory instances
#     It includes all fields from the ProductSubCategory model.
#     """

#     class Meta:
#         model = ProductSubCategory
#         fields = "__all__"


# class ProductChildCategoryForm(forms.ModelForm):
#     """
#     Form for Product Child Category
#     This form is used to create or update ProductChildCategory instances.
#     It includes all fields from the ProductChildCategory model.
#     """

#     class Meta:
#         model = ProductChildCategory
#         fields = "__all__"


# class AttributeListForm(forms.ModelForm):
#     """
#     Form for Attribute List
#     This form is used to create or update AttributeList instances.
#     It includes all fields from the AttributeList model.
#     """

#     class Meta:
#         model = AttributeList
#         fields = "__all__"


# class AttributeValueListForm(forms.ModelForm):
#     """
#     Form for Attribute Value List
#     This form is used to create or update AttributeValueList instances.
#     It includes all fields from the AttributeValueList model.
#     """

#     class Meta:
#         model = AttributeValueList
#         fields = "__all__"
