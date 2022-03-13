from django.db.models.fields.related import OneToOneField
from rest_framework.serializers import  ModelSerializer
from rest_framework.fields import CurrentUserDefault

from .models import *


class ProfileCreateSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ['email','password']
        