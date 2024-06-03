from rest_framework import serializers, status
from django.contrib.auth.models import User
from .models import ParkOwner, Zone, Booking, Vehicle, Subscription, Employee, Slot, Salary
from django.db.models import Q
from datetime import timedelta, date


class ParkownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParkOwner
        fields = '__all__'
class UserDetailsSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id','username','email', 'first_name', 'last_name']

class ParkownerProfileSerializer(serializers.ModelSerializer):
    park_owner_id = UserDetailsSerializer()
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
    employee = UserDetailsSerializer()
    class Meta:
        model = Employee
        fields = '__all__'
        

class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['id', 'employee', 'amount', 'is_paid',
                  'payment_date', 'effective_from', 'effective_to']
        read_only_fields = ['payment_date', 'is_paid']


class SalaryPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = ['id','effective_from', 'effective_to']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('employee', {})
        user_instance = instance.employee

        
        for attr, value in user_data.items():
            setattr(user_instance, attr, value)
        user_instance.save()

        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class EmployeeRegistrationSerializer(serializers.ModelSerializer):
    mobile_no = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(write_only=True, required=True)
    joined_date = serializers.DateTimeField(write_only=True, required=False)
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
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'error': "Username already exists"})
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
        employee.is_active = True
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
    login = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        login = data.get('login')
        password = data.get('password')

        if login and password:
            user = User.objects.filter(
                Q(username=login) | Q(email=login) | Q(
                    customer__mobile_no=login)
            ).first()

            if user and user.check_password(password):
                return data
            else:
                raise serializers.ValidationError(
                    "Incorrect login or password.",
                    code='invalid_credentials'
                )
        else:
            raise serializers.ValidationError(
                "Both login and password are required.",
                code='missing_credentials'
            )


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id','park_owner', 'name', 'capacity', 'created_at']


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
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = ['id','employee','customer','zone', 'slot', 'vehicle', 'ticket_no',
                  'amount', 'fine', 'check_in_time', 'check_out_time', 'rate_per_minute', 'booking_time', 'appoximate_check_out_time', 'total_amount','is_paid']
        read_only_fields = ['ticket_no', 'rate_per_minute', 'fine', 'is_paid']

    def get_ticket_no(self, instance):
        return instance.ticket_no()

    def create(self, validated_data):
        vehicle_data = validated_data.pop('vehicle')
        vehicle_instance = Vehicle.objects.create(**vehicle_data)
        booking_instance = Booking.objects.create(vehicle=vehicle_instance, **validated_data)
        return booking_instance
    
    def update(self, instance, validated_data):
        vehicle_data = validated_data.pop('vehicle', None)
        if vehicle_data:
            # Update the nested vehicle instance
            vehicle_instance = instance.vehicle
            for attr, value in vehicle_data.items():
                setattr(vehicle_instance, attr, value)
            vehicle_instance.save()
        
        # Update Booking instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance

    #     model = Booking
    #     fields = ['zone', 'slot', 'time_slot', 'vehicle', 'ticket_no',
    #               'amount', 'fine', 'check_in_time', 'check_out_time']
    #     read_only_fields = ['ticket_no', 'slot']

    # def get_ticket_no(self, obj):
    #     return obj.ticket_no()

    # def create(self, validated_data):
    #     vehicle_data = validated_data.pop('vehicle')
    #     vehicle = Vehicle.objects.create(**vehicle_data)

    #     # Create the booking instance
    #     booking = Booking(vehicle=vehicle, **validated_data, status=True)

    #     # Assign the slot before saving
    #     booking.slot = booking.find_next_available_slot()
    #     if booking.slot is None:
    #         raise serializers.ValidationError(
    #             "No available slots in the selected zone.")

    #     booking.save()
    #     return booking

    # def validate(self, data):
    #     # Check if the selected slot is already booked
    #     slot = data.get('slot')
    #     if slot and Booking.objects.filter(slot=slot, status=True).exists():
    #         raise serializers.ValidationError("This slot is already booked.")
    #     return data


class SubscriptionPackageAdmin(serializers.ModelSerializer):

    list_display = ('name', 'duration_months', 'price', 'discount')


class SubscriptionSerializer(serializers.ModelSerializer):
    # Read-only field for amount
    amount = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = ['id', 'package', 'start_date', 'end_date', 'amount']
        # Exclude read-only fields when creating instances
        extra_kwargs = {
            'end_date': {'read_only': True},
            'total_amount': {'read_only': True},
        }

    def create(self, validated_data):
        # Calculate the end_date based on the package duration
        package = validated_data.get('package')
        duration_days = package.duration_days
        end_date = validated_data['start_date'] + timedelta(days=duration_days)
        validated_data['end_date'] = end_date

        instance = Subscription.objects.create(**validated_data)
        return instance

class BookingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'total_amount', 'check_in_time', 'check_out_time','fine']


class ZoneSummarySerializer(serializers.ModelSerializer):
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = ['id', 'name', 'capacity', 'available_slots']

    def get_available_slots(self, obj):
        return Slot.objects.filter(zone=obj, available=True).count()
