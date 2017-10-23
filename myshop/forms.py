from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
User = get_user_model()

# class UserLoginForm(forms.Form):
#     email = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     def clean(self):
#         email = self.cleaned_data.get("email")
#         password = self.cleaned_data.get("password")
#         user_qs = User.objects.filter(email=email)
#         if user_qs.count() == 1:
#             user= user_qs.first()
#
#         if not user:
#             raise forms.ValidationError("This User Does not Exist")
#         if not user.check_password(password):
#             raise forms.ValidationError("Incorrect Password")
#         if not user.is_active:
#             raise forms.ValidationError("This user no longer active")
#         return super(UserLoginForm, self).clean()


class UserResgisterForm(UserCreationForm):
    username = forms.CharField(max_length=20, help_text="")
    password1 = forms.CharField(max_length=20, widget=forms.PasswordInput)
    password1 = forms.CharField( max_length=20, widget=forms.PasswordInput)
    email = forms.EmailField(max_length=254, help_text='')
    full_name = forms.CharField(max_length=20)
    city = forms.CharField(max_length=20)
    pincode = forms.IntegerField()
    address1 = forms.CharField(max_length=100)
    address2 = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=10)
    country = forms.CharField(max_length=20)
    class Meta:
        model = User
        fields = ['username','password1', 'password2', 'email', 'full_name', 'city', 'pincode', 'address1', 'address2', 'phone', 'country', ]

# class CustomerForm(forms.ModelForm):
#     class Meta:
#             model=Customer
#             fields=[
#                 "full_name",
#                 "city",
#                 "pincode",
#                 "address1",
#                 "address2",
#                 "phone",
#                 "country",
#             ]
