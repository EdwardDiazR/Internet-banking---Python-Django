from django.forms import ModelForm
from django import forms
from .models import Usuario


class SignUpForm(ModelForm):
    confirm_pass = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['username','userCIF','user_name','user_lastName','user_email','user_password','confirm_pass','user_phone' ]


class LoginForm(forms.Form):
    
    username= forms.CharField(max_length=100,label="Usuario",required=True)
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña",required=True)