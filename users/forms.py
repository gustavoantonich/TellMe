from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico', 'required': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Contraseña', 'required': True})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirmar contraseña', 'required': True})
        for field in self.fields.values():
            field.help_text = None


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Usuario', 'required': True})
        self.fields['password'].widget.attrs.update({'placeholder': 'Contraseña', 'required': True})


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'avatar', 'location', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
