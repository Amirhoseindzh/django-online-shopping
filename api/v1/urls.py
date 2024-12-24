from django.urls import path, include

urlpatterns = [
    path('accounts/', include('api.v1.accounts.urls')),
    path('shop/', include('api.v1.shop.urls')),
]