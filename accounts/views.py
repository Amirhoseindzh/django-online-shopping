from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import FormView, View
from django.contrib import messages
from django.core.mail import send_mail
from allauth.account.views import LoginView, LoginForm


class CustomLoginView(LoginView):
    template_name = "account/login.html" 
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy("profile")





