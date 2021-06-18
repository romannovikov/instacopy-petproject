from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from .models import Profile

User = get_user_model()


class UserSignupForm(SignupForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": _("Full Name"), }),
        max_length=16,
        required=True,
    )

    def signup(self, request, user):
        user.full_name = self.cleaned_data['full_name']
        user.save()
        return user


class UserLoginForm(LoginForm):
    pass


class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo', 'website', 'phone_number', 'gender', 'bio',)
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'file-input'}),
            'bio': forms.Textarea(attrs={'class': 'textarea is-small', 'rows': '5'}),
            'website': forms.URLInput(attrs={'class': 'input'}),
            'phone_number': forms.TextInput(attrs={'class': 'input', 'type': 'tel'}),
            'gender': forms.Select(),
        }
