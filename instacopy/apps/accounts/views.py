from allauth.account.views import (
    LoginView,
    SignupView,
    PasswordResetView,
    PasswordResetFromKeyView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from . import forms
from .models import Profile

User = get_user_model()


class UserSignupView(SignupView):
    model = User
    success_url = reverse_lazy('account_login')
    form_class = forms.UserSignupForm
    template_name = 'accounts/signup.html'


signup = UserSignupView.as_view()


class UserLoginView(LoginView):
    form_class = forms.UserLoginForm
    template_name = 'accounts/login.html'


login = UserLoginView.as_view()


class UserLogoutView(LogoutView):
    pass


logout = UserLogoutView.as_view()


class UserPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"


password_reset = UserPasswordResetView.as_view()


class UserPasswordResetDoneView(TemplateView):
    template_name = "accounts/password_reset_done.html"


password_reset_done = UserPasswordResetDoneView.as_view()


class UserPasswordResetFromKeyView(PasswordResetFromKeyView):
    template_name = "accounts/password_reset_from_key.html"


password_reset_from_key = UserPasswordResetFromKeyView.as_view()


class UserPasswordResetFromKeyDoneView(TemplateView):
    template_name = "accounts/password_reset_from_key_done.html"


password_reset_from_key_done = UserPasswordResetFromKeyDoneView.as_view()


class AccountSettingsView(UpdateView):
    model = Profile
    success_url = reverse_lazy('feed')
    form_class = forms.ProfileSettingsForm
    template_name = 'accounts/account_settings.html'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


account_settings = AccountSettingsView.as_view()
