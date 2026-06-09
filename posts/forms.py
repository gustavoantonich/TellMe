from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Que esta pasando?',
                'rows': 3,
            }),
            'image': forms.URLInput(attrs={
                'placeholder': 'URL de una imagen (opcional)',
            }),
        }
