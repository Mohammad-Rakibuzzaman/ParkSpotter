from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ParkOwner


class RegistrationSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    payment_date = serializers.DateField(write_only=True, required=True)
    image = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = ParkOwner
        fields = ['username', 'first_name', 'last_name', 'mobile_no',
                  'nid_card_no', 'email', 'password', 'confirm_password', 'slot_size', 'capacity', 'address', 'area', 'payment_method', 'card_no', 'amount', 'payment_date','image']

    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        email = self.validated_data['email']
        password = self.validated_data['password']
        password2 = self.validated_data['confirm_password']
        mobile_no = self.validated_data['mobile_no']
        nid_card_no = self.validated_data['nid_card_no']
        slot_size = self.validated_data['slot_size']
        capacity = self.validated_data['capacity']
        address = self.validated_data['address']
        area = self.validated_data['area']
        payment_method = self.validated_data['payment_method']
        card_no = self.validated_data['card_no']
        payment_date = self.validated_data['payment_date']
        image = self.validated_data.get('image', None)

        if password != password2:
            raise serializers.ValidationError(
                {'error': "Password Doesn't Matched"})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'error': "Email Already exists"})
        if ParkOwner.objects.filter(mobile_no=mobile_no).exists():
            raise serializers.ValidationError(
                {'error': "This mobile number is already in use"})

        user = User(username=username, email=email,
                    first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.is_active = False
        user.save()
        ParkOwner.objects.create(user=user, mobile_no=mobile_no,
                                 id=user.id, nid_card_no=nid_card_no, address=address, slot_size=slot_size, capacity=capacity, area=area, payment_method=payment_method, card_no=card_no, payment_date=payment_date, image=image)

        return user
