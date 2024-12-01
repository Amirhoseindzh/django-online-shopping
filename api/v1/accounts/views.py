from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    )
from accounts.models import Profile, Address
from .serializers import (
    ProfileSerializer,
    AddressSerializer,
    )

User = get_user_model()
    

class ProfileView(RetrieveUpdateAPIView):
    """ 
    API endpoint that allows users to retrieve or update their profile.
    """
    queryset = Profile.objects.select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the profile of the authenticated user
        return self.get_queryset().first()

      
class AddressViewSet(ModelViewSet):
    """
    API endpoint to manage user addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Restrict the queryset to addresses of the authenticated user
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate the address with the authenticated user
        serializer.save(user=self.request.user)