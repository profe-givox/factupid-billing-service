import random
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django import forms



from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requerido. Proporciona una dirección de correo electrónico válida.')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=100, label='Correo electrónico o Nombre de usuario')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')



class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Username'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class SendEmailResetPasswordForm(forms.Form):
    email = forms.EmailField(max_length=254, label='Correo electrónico')

class ResetPasswordForm2(forms.Form):
    password = forms.CharField(max_length=254,widget=forms.PasswordInput, label='Nueva contraseña')
    password2 = forms.CharField(max_length=254,widget=forms.PasswordInput, label='Confirmar contraseña')
    
    