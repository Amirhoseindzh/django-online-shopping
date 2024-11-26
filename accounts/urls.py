from django.urls import path
from django.contrib.auth import views as auth_views

from .views import UserProfile
from .views import CustomLoginView
from .views import address_list


urlpatterns = [
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('accounts/profile/', UserProfile.as_view(), name='profile'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # addresses urls
    path("addresses/", address_list, name="address_list"),
]