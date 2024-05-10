from rest_framework import serializers
from django.contrib.auth.models import User

from .models import ParkOwner


class RegistrationSerializer(serializers.ModelSerializer):

    image = serializers.ImageField(required=True, write_only=True)
    mobile_no = serializers.CharField(required=True, write_only=True)
    address = serializers.CharField(required=True, write_only=True)



