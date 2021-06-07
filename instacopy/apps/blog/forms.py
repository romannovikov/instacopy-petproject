from django import forms

from .models import Post


class PostCreationForm(forms.ModelForm):
    media = forms.ImageField(required=True)
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'input is-medium'}), required=True)

    class Meta:
        model = Post
        fields = ('media', 'text')
