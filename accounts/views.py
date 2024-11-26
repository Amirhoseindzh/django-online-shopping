from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from allauth.account.views import LoginView, LoginForm
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import Profile, Address

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = "account/login.html" 
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse_lazy("profile")


class UserProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "account-profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("profile")

    def get_object(self):
        # Retrieve the Profile instance associated with the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def get_form_kwargs(self):
        # Pass the 'user' instance to the form to handle User fields
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Add user to the form kwargs
        return kwargs
    
    
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'account-addresses.html', {'addresses': addresses})

