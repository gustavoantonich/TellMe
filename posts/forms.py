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
                'maxlength': 500,
                'class': 'post-content',
            }),
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
            }),
        }
