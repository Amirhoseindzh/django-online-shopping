from rest_framework import serializers
from rest_framework.serializers import HyperlinkedModelSerializer, ModelSerializer
from django.contrib.auth import get_user_model
from accounts.models import Profile, Address
from shop.models import States

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for nested User fields."""
    class Meta:
        model = User
        fields = ['id', 'username', 'phone']
        extra_kwargs = {
            'username': {'required': False},  # Make email optional for updates
            'phone': {'required': False},  # Make email optional for updates
        }
        
    def update(self, instance, validated_data):
        # Update only provided fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
    
    
class ProfileSerializer(ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Profile
        fields = [
        'id',
        'user',
        'first_name',
        'last_name',
        'age',
        'gender',
        'description',
        'newsletter',
        'avatar'
    ]

    
    def update(self, instance, validated_data):
        # Extract and handle user data separately
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update profile fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
    
           
        
class AddressSerializer(HyperlinkedModelSerializer):
    state = serializers.PrimaryKeyRelatedField(queryset=States.objects.all())
    user = serializers.SerializerMethodField('get_user')
    
    class Meta:
        model = Address
        fields = [
        'id',
        'user',
        'postal_address',
        'full_name',
        'phone_number',
        'neighborhood',
        'city',
        'state',
        'postal_code',
        'license_plate',
        'unit',
        'is_default',
        ]

    def get_user(self, obj):
        # Customize the display of the user field
        return obj.user.username
    