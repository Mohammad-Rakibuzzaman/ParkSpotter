from rest_framework import serializers, status
from django.contrib.auth.models import User
from .models import ParkOwner, Zone, Booking, Vehicle, Subscription, Employee,Slot


class ParkownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkOwner
        fields = '__all__'
class ParkownerDetailsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id','username','email', 'first_name', 'last_name']

class ParkownerProfileSerializer(serializers.ModelSerializer):
    park_owner_id = ParkownerDetailsSerializer()
    class Meta:
        model = ParkOwner
        fields = '__all__'
    def update(self, instance, validated_data):
        user_data = validated_data.pop('park_owner_id', {})
        user_serializer = self.fields['park_owner_id']
        user_instance = instance.park_owner_id
        user_instance = user_serializer.update(user_instance, user_data)
        
        instance.image = validated_data.get('image', instance.image)
        instance.mobile_no = validated_data.get('mobile_no', instance.mobile_no)
        instance.address = validated_data.get('address', instance.address)
        
        instance.save()
        return instance


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(write_only=True, required=True)
    joined_date = serializers.DateTimeField(write_only=True, required=True)
    class Meta:
        model = Employee
        fields = ['username', 'first_name', 'last_name','qualification', 'mobile_no',
                  'nid_card_no', 'email', 'password', 'confirm_password','address','joined_date']
        extra_kwargs = {
            'is_active': {'read_only': True},  
        }
    def save(self):
        username = self.validated_data['username']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        qualification = self.validated_data['qualification']
        email = self.validated_data['email']
        password = self.validated_data['password']
        password2 = self.validated_data['confirm_password']
        mobile_no = self.validated_data['mobile_no']
        nid_card_no = self.validated_data['nid_card_no']
        address = self.validated_data['address']
        joined_date = self.validated_data['joined_date']
        

        if password != password2:
            raise serializers.ValidationError(
                {'error': "Password Doesn't Matched"})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'error': "Email Already exists"})
        if Employee.objects.filter(mobile_no=mobile_no).exists():
            raise serializers.ValidationError(
                {'error': "This mobile number is already in use"})
        
        user = self.context['request'].user  # Getting the logged-in user
        try:
            park_owner = ParkOwner.objects.get(park_owner_id=user)
        except ParkOwner.DoesNotExist:
            raise serializers.ValidationError(
                {'error': "Logged in user is not a ParkOwner"})

        employee = User(username=username, email=email,
                    first_name=first_name, last_name=last_name)
        employee.set_password(password)
        employee.is_active = False
        employee.save()
        Employee.objects.create(employee=employee, mobile_no=mobile_no,
                                 id=employee.id, nid_card_no=nid_card_no, address=address, qualification=qualification, joined_date=joined_date, park_owner_id= park_owner)

        return employee


class RegistrationSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    payment_date = serializers.DateField(write_only=True, required=False)
    image = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = ParkOwner
        fields = ['username', 'first_name', 'last_name', 'mobile_no',
                  'nid_card_no', 'email', 'password', 'confirm_password', 'slot_size', 'capacity', 'address', 'area', 'payment_method', 'amount', 'payment_date', 'image']

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
        amount = self.validated_data['amount']
        payment_date = self.validated_data['payment_date']
        image = self.validated_data.get('image', None)

        if password != password2:
            raise serializers.ValidationError(
                {'error': "Password Doesn't Matched"})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'error': "Username already exists"})
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
        ParkOwner.objects.create(park_owner_id=user, mobile_no=mobile_no,
                                 id=user.id, nid_card_no=nid_card_no, address=address, slot_size=slot_size, capacity=capacity, area=area, payment_method=payment_method, payment_date=payment_date, image=image, amount=amount)

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = User.objects.filter(username=username).first()

            if user and user.check_password(password):
                return data
            else:
                raise serializers.ValidationError(
                    "Incorrect username or password.",
                    code='invalid_credentials',
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
        else:
            raise serializers.ValidationError(
                "Both username and password are required.",
                code='missing_credentials',
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['park_owner', 'name', 'capacity', 'created_at']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['plate_number', 'mobile_no']


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = ['id', 'slot_number', 'zone', 'available']


class BookingSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    ticket_no = serializers.SerializerMethodField()
    amount = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['zone', 'slot', 'time_slot', 'vehicle', 'ticket_no',
                  'amount', 'fine', 'check_in_time', 'check_out_time']
        read_only_fields = ['ticket_no', 'slot']

    def get_ticket_no(self, obj):
        return obj.ticket_no()

    def create(self, validated_data):
        vehicle_data = validated_data.pop('vehicle')
        vehicle = Vehicle.objects.create(**vehicle_data)

        # Create the booking instance
        booking = Booking(vehicle=vehicle, **validated_data, status=True)

        # Assign the slot before saving
        booking.slot = booking.find_next_available_slot()
        if booking.slot is None:
            raise serializers.ValidationError(
                "No available slots in the selected zone.")

        booking.save()
        return booking

    def validate(self, data):
        # Check if the selected slot is already booked
        slot = data.get('slot')
        if slot and Booking.objects.filter(slot=slot, status=True).exists():
            raise serializers.ValidationError("This slot is already booked.")
        return data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'package', 'start_date', 'end_date', 'amount']

    # Read-only field for amount
    amount = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()

    def create(self, validated_data):
        instance = Subscription(**validated_data)
        instance.save()
        return instance
