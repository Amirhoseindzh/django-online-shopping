from django.urls import path
from django.contrib.auth import views as auth_views

from shop.views import Profile
from .views import CustomLoginView

urlpatterns = [
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('accounts/profile/', Profile.as_view(), name='profile'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]