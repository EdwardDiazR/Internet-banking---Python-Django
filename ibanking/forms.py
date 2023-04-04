from django.forms import ModelForm
from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password,check_password


class SignUpForm(ModelForm):
    confirm_pass = forms.CharField(widget=forms.PasswordInput(), label="Confirmar contraseña",required=True)
    user_password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña",required=True)



    class Meta:
        model = Usuario
        fields = ['username','userCIF','user_name','user_lastName','user_email','user_password','confirm_pass','user_phone' ]

class LoginForm(forms.Form):
    
    username= forms.CharField(max_length=100,label="Usuario",required=True)
    password = forms.CharField(widget=forms.PasswordInput(), label="Contraseña",required=True)