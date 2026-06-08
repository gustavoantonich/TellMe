from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    pass


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('bio', 'avatar', 'location', 'website')