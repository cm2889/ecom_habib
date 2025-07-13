from django import forms

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
