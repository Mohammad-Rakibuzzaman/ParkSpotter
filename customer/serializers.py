from rest_framework import serializers, status
from django.contrib.auth.models import User

from accounts.serializers import UserDetailsSerializer
from . models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    customer_id = UserDetailsSerializer()
    class Meta:
        model = Customer
        fields = '__all__'

    def update(self, instance, validated_data):
        user_data = validated_data.pop('customer_id', {})
        user_instance = instance.customer_id

        
        for attr, value in user_data.items():
            setattr(user_instance, attr, value)
        user_instance.save()

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    joined_date = serializers.DateTimeField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = ['username', 'first_name', 'last_name', 'mobile_no',
                  'email', 'password', 'confirm_password', 'joined_date']
        extra_kwargs = {
            'is_active': {'read_only': True},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        if Customer.objects.filter(mobile_no=data['mobile_no']).exists():
            raise serializers.ValidationError(
                "This mobile number is already in use.")
        return data

    def create(self, validated_data):
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        email = validated_data['email']
        password = validated_data['password']
        mobile_no = validated_data['mobile_no']

        user = User.objects.create_user(
            username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        customer = Customer.objects.create(id=user.id, customer_id=user, mobile_no=mobile_no)
        return customer
