from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# from .models import Customer
class SignUpForm(forms.ModelForm):
    
    #لا تُحفظ مباشرة
    password = forms.CharField(widget=forms.PasswordInput, validators=[validate_password])
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    phone = forms.CharField(max_length=15, label="Phone")
    address = forms.CharField(max_length=255, label="Address")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']  

    def clean_username(self):
        username = self.cleaned_data.get('username')
        forbidden_usernames = ['admin', 'root', 'superuser']
        if username.lower() in forbidden_usernames or User.objects.filter(username=username).exists():
            # رسالة عامة لتجنب كشف التفاصيل
            raise ValidationError("اسم المستخدم غير متاح.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "كلمات المرور غير متطابقة.")




class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
