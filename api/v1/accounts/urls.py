from django.urls import include, path
from rest_framework import routers

from .views import (
    ProfileView,
    AddressViewSet,
    )

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('profiles/', ProfileView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]