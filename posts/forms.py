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

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('La imagen no puede superar los 5MB')
        return image
