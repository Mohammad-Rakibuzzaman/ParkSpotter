from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Sum
#12-5 added by rtz
from .serializers import SlotSerializer, ZoneSerializer, BookingSerializer, VehicleSerializer,SalarySerializer, SalaryPaymentSerializer, BookingSummarySerializer, ZoneSummarySerializer, EmployeeSerializer, SubscriptionPackageSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
# for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics
#rtz added 12-5
from .models import ParkOwner, Slot, Zone, Booking, Vehicle, Employee, Salary,SubscriptionPackage
from customer.models import Customer
from django.db.models import Q
from datetime import datetime, timedelta

# Create your views here.
class ParkownerProfileViewset(viewsets.ModelViewSet):
    queryset = ParkOwner.objects.all()
    serializer_class = serializers.ParkownerProfileSerializer


class EmployeeProfileViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

    @action(detail=True, methods=['post'])
    def pay_salary(self, request, pk=None):
        salary = self.get_object()
        if salary.is_paid:
            return Response({"detail": "Salary already paid."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SalaryPaymentSerializer(data=request.data)
        if serializer.is_valid():
            effective_from = serializer.validated_data.get('effective_from')
            effective_to = serializer.validated_data.get('effective_to')

            # Update the salary fields
            salary.effective_from = effective_from
            salary.effective_to = effective_to
            salary.is_paid = True
            salary.payment_date = timezone.now()
            salary.save()

            return Response(SalarySerializer(salary).data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParkownerProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = models.ParkOwner.objects.all()
    serializer_class = serializers.ParkownerProfileSerializer
    lookup_field = 'park_owner_id__id'

class UserRegistrationApiView(APIView):
    serializer_class = serializers.RegistrationSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            current_site = get_current_site(request)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            confirm_link = f"{request.scheme}://{current_site.domain}/accounts/active/{uid}/{token}"
            email_subject = "Confirm Your Email"
            email_body = render_to_string('confirm_email.html', {'confirm_link' : confirm_link})
            
            email = EmailMultiAlternatives(email_subject , '', to=[user.email])
            email.attach_alternative(email_body, "text/html")
            email.send()
            return Response("Check your mail for confirmation")
        return Response(serializer.errors)


def activate(request, uid64, token):
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://development-parkspotter.netlify.app/login')
    else:
        return redirect('https://development-parkspotter.netlify.app/login')
    

class EmployeeRegistrationView(generics.CreateAPIView):
    serializer_class = serializers.EmployeeRegistrationSerializer
    # permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def perform_create(self, serializer):
        employee = serializer.save()
        employee.is_active = True  
        employee.save()
    

class UserLoginApiView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=self.request.data)

        if serializer.is_valid():
            login_field = serializer.validated_data['login']
            password = serializer.validated_data['password']

            # Authenticate using the custom backend
            user = authenticate(
                request, username=login_field, password=password)
            if user is None:
                try:
                    user = User.objects.get(
                        Q(username=login_field) | Q(email=login_field) | Q(
                            customer__mobile_no=login_field)
                    )
                    if not user.check_password(password):
                        user = None
                except User.DoesNotExist:
                    user = None

            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                login(request, user)

                is_park_owner = ParkOwner.objects.filter(
                    park_owner_id=user).exists()
                is_employee = Employee.objects.filter(employee=user).exists()
                is_customer = Customer.objects.filter(
                    customer_id=user).exists()
                is_admin = user.is_staff  # Check if user is an admin

                if is_admin:
                    return Response({
                        'token': token.key,
                        'user_id': user.id,
                        'role': 'admin'
                    })
                elif is_park_owner:
                    return Response({
                        'token': token.key,
                        'user_id': user.id,
                        'role': 'park_owner'
                    })
                elif is_employee:
                    return Response({
                        'token': token.key,
                        'user_id': user.id,
                        'role': 'employee'
                    })
                elif is_customer:
                    return Response({
                        'token': token.key,
                        'user_id': user.id,
                        'role': 'customer'
                    })
                else:
                    return Response(
                        {"detail": "User role not defined."},
                        status=status.HTTP_403_FORBIDDEN
                    )

            return Response({'error': "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')
    
#12.5 rtzaddedd


class ZoneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ZoneSerializer

    def get_queryset(self):
        user = self.request.user

        # Check if the user is a ParkOwner
        if ParkOwner.objects.filter(park_owner_id=user).exists():
            park_owner = ParkOwner.objects.get(park_owner_id=user)
            return Zone.objects.filter(park_owner=park_owner)

        # Check if the user is an Employee
        if Employee.objects.filter(employee=user).exists():
            employee = Employee.objects.get(employee=user)
            return Zone.objects.filter(park_owner=employee.park_owner_id)

        # Check if the user is a Customer
        if Customer.objects.filter(customer_id=user).exists():
            park_owner = self.request.query_params.get('park_owner')
            if park_owner:
                return Zone.objects.filter(park_owner=park_owner)

        return Zone.objects.none()

class SlotAPIView(viewsets.ModelViewSet):
    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    # def update(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         instance.check_out_time = timezone.now()
    #         instance.status = False
    #         instance.slot.available = True
    #         instance.slot.save()
    #         instance.calculate_fine()  # Calculate fine if applicable
    #         instance.save()

    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Booking.DoesNotExist:
    #         return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     except Slot.DoesNotExist:
    #         return Response({'error': 'Slot not found.'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPackageViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPackage.objects.all()
    serializer_class = SubscriptionPackageSerializer


# class SubscriptionViewSet(viewsets.ModelViewSet):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionSerializer


def nearby_parking_lots(request):
    park_owners = ParkOwner.objects.all()
    return render(request, 'nearby_parking_lots.html', {
        'park_owners': park_owners,
    })


class ParkOwnerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        try:
            park_owner = ParkOwner.objects.get(park_owner_id=user)
        except ParkOwner.DoesNotExist:
            return Response({"error": "You are not a ParkOwner."}, status=status.HTTP_403_FORBIDDEN)

        # Get date filters from request
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        start_date = end_date = None

        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(
                    start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter bookings based on date range
        bookings = Booking.objects.filter(zone__park_owner=park_owner)
        if start_date and end_date:
            bookings = bookings.filter(
                booking_time__date__gte=start_date,
                booking_time__date__lte=end_date
            )
        booking_serializer = BookingSummarySerializer(bookings, many=True)

        # Filter salaries based on date range
        employees = Employee.objects.filter(park_owner_id=park_owner)
        employee_serializer = EmployeeSerializer(employees, many=True)
        salaries = Salary.objects.filter(employee__in=employees)
        if start_date and end_date:
            salaries = salaries.filter(
                payment_date__gte=start_date,
                payment_date__lte=end_date
            )
        salary_serializer = SalarySerializer(salaries, many=True)

        # Get zone summary
        zones = Zone.objects.filter(park_owner=park_owner)
        zone_serializer = ZoneSummarySerializer(zones, many=True)

        # Total earnings
        total_earnings = sum(booking.total_amount for booking in bookings)
        total_salary_cost = sum(salary.amount for salary in salaries)
        net_revenue = total_earnings - total_salary_cost

        # Total bookings and employees
        total_bookings = bookings.count()
        total_employees = employees.count()

        # Customer details
        park_owner_customers = Customer.objects.filter(
            booking__zone__park_owner=park_owner).distinct()
        customer_details = []
        best_customer = None
        max_booking_time = timedelta(0)

        for customer in park_owner_customers:
            customer_bookings = bookings.filter(customer=customer)
            bookings_info = [{
                "booking_id": booking.id,
                "vehicle": booking.vehicle.plate_number,
                "slot": booking.slot.slot_number,
                "check_in_time": booking.check_in_time,
                "check_out_time": booking.check_out_time,
                "total_amount": booking.total_amount
            } for booking in customer_bookings]

            # Initialize total_booking_time as a timedelta object
            total_booking_time = timedelta(0)

            for booking in customer_bookings:
                if booking.check_in_time and booking.check_out_time:
                    total_booking_time += (booking.check_out_time -
                                           booking.check_in_time)

            if total_booking_time > max_booking_time:
                max_booking_time = total_booking_time
                best_customer = {
                    "id": customer.id,
                    "mobile_no": customer.mobile_no,
                    "total_booking_time": max_booking_time,
                    "total_booking_amount": sum(booking.total_amount for booking in customer_bookings),
                }

            customer_details.append({
                "id": customer.id,
                "mobile_no": customer.mobile_no,
                "booking_count": customer_bookings.count(),
                "total_booking_amount": sum(booking.total_amount for booking in customer_bookings),
                "bookings": bookings_info
            })

        total_customers = park_owner_customers.count()

        # Employee-based booking details
        employee_details = []
        for employee in employees:
            employee_bookings = bookings.filter(employee=employee)
            employee_booking_count = employee_bookings.count()
            employee_total_amount = sum(
                booking.total_amount for booking in employee_bookings)
            employee_bookings_info = [{
                "booking_id": booking.id,
                "vehicle": booking.vehicle.plate_number,
                "slot": booking.slot.slot_number,
                "check_in_time": booking.check_in_time,
                "check_out_time": booking.check_out_time,
                "total_amount": booking.total_amount
            } for booking in employee_bookings]

            employee_details.append({
                "id": employee.id,
                "booking_count": employee_booking_count,
                "total_booking_amount": employee_total_amount,
                "bookings": employee_bookings_info
            })

        dashboard_data = {
            "total_earnings": total_earnings,
            "total_bookings": total_bookings,
            "employees": employee_serializer.data,
            "bookings": booking_serializer.data,
            "zones": zone_serializer.data,
            "total_salary_cost": total_salary_cost,
            "net_revenue": net_revenue,
            "total_employees": total_employees,
            "total_customers": total_customers,
            "customers": customer_details,
            "best_customer": best_customer,
            "employee_details": employee_details
        }

        return Response(dashboard_data)

class AdminDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Get all ParkOwners
        park_owners = ParkOwner.objects.all()

        # Filter ParkOwners with and without subscription
        park_owners_with_subscription = park_owners.filter(
            subscription_id__isnull=False)
        park_owners_without_subscription = park_owners.filter(
            subscription_id__isnull=True)

        total_earnings = 0
        total_salary_cost = 0

        park_owners_with_subscription_data = []
        for park_owner in park_owners_with_subscription:
            # Calculate total earnings for the current ParkOwner
            park_owner_bookings = Booking.objects.filter(
                zone__park_owner=park_owner)
            earnings = sum(
                booking.total_amount for booking in park_owner_bookings)
            total_earnings += earnings

            # Calculate total salary cost for the current ParkOwner
            salary_cost_aggregate = Salary.objects.filter(
                employee__park_owner_id=park_owner).aggregate(total=Sum('amount'))
            salary_cost = salary_cost_aggregate['total'] or 0
            total_salary_cost += salary_cost

            # Calculate net revenue for the current ParkOwner
            park_owner_net_revenue = earnings - salary_cost

            # Include subscription details
            subscription = park_owner.subscription_id
            subscription_data = {
                "name": subscription.name,
                "amount": subscription.amount,
                "discount": subscription.discount,
                "total_amount": subscription.total_amount,
            } if subscription else {}

            # Calculate customer count and details
            park_owner_customers = Customer.objects.filter(
                booking__zone__park_owner=park_owner).distinct()
            customer_count = park_owner_customers.count()

            customer_details = []
            for customer in park_owner_customers:
                # Get booking information for the customer
                customer_bookings = Booking.objects.filter(customer=customer)
                bookings_info = [{
                    "booking_id": booking.id,
                    "vehicle": booking.vehicle.plate_number,
                    "slot": booking.slot.slot_number,
                    "check_in_time": booking.check_in_time,
                    "check_out_time": booking.check_out_time,
                    "total_amount": booking.total_amount
                } for booking in customer_bookings]

                customer_details.append({
                    "id": customer.id,
                    "mobile_no": customer.mobile_no,
                    "booking_count": customer_bookings.count(),
                    "total_booking_amount": sum(booking.total_amount for booking in customer_bookings),
                    "bookings": bookings_info
                })

            # Append data to the list
            park_owners_with_subscription_data.append({
                "park_owner_id": park_owner.id,
                "username": park_owner.park_owner_id.username,
                "total_earnings": earnings,
                "total_salary_cost": salary_cost,
                "park_owner_net_revenue": park_owner_net_revenue,
                "subscription": subscription_data,
                "customer_count": customer_count,
                "customers": customer_details
            })

        # List of park owners without a subscription
        park_owners_without_subscription_data = [
            {"park_owner_id": park_owner.id,
                "username": park_owner.park_owner_id.username}
            for park_owner in park_owners_without_subscription
        ]

        # Calculate net revenue as the total of Subscription.amount
        total_subscription_amount = sum(
            subscription.amount for subscription in SubscriptionPackage.objects.all())

        # Calculate conversion ratio
        total_park_owners = park_owners.count()
        park_owners_with_subscription_count = park_owners_with_subscription.count()
        conversion_ratio = (park_owners_with_subscription_count /
                            total_park_owners) * 100 if total_park_owners > 0 else 0

        admin_dashboard_data = {
            "park_owners_with_subscription": park_owners_with_subscription_data,
            "total_earnings": total_subscription_amount,
            "net_revenue": total_subscription_amount,
            "conversion_ratio": conversion_ratio,
            "park_owners_without_subscription": park_owners_without_subscription_data,
            "park_owners_with_subscription_count": park_owners_with_subscription_count,
            "park_owners_without_subscription_count": park_owners_without_subscription.count()
        }

        return Response(admin_dashboard_data)


class UserActivationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user_type = request.data.get('user_type')
        try:
            user = User.objects.get(pk=pk)
            if user_type == 'park_owner':
                park_owner = ParkOwner.objects.get(park_owner_id=user)
                # Activate the park owner
                user.is_active = True
                user.save()
                return Response({"message": "Park owner activated successfully."})
            elif user_type == 'customer':
                customer = Customer.objects.get(customer_id=user)
                # Activate the customer
                user.is_active = True
                user.save()
                return Response({"message": "Customer activated successfully."})
            elif user_type == 'employee':
                employee = Employee.objects.get(employee=user)
                # Activate the employee
                user.is_active = True
                user.save()
                return Response({"message": "Employee activated successfully."})
            else:
                return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, ParkOwner.DoesNotExist, Customer.DoesNotExist, Employee.DoesNotExist):
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user_type = request.data.get('user_type')
        try:
            user = User.objects.get(pk=pk)
            if user_type == 'park_owner':
                park_owner = ParkOwner.objects.get(park_owner_id=user)
                # Deactivate the park owner
                user.is_active = False
                user.save()
                return Response({"message": "Park owner deactivated successfully."})
            elif user_type == 'customer':
                customer = Customer.objects.get(customer_id=user)
                # Deactivate the customer
                user.is_active = False
                user.save()
                return Response({"message": "Customer deactivated successfully."})
            elif user_type == 'employee':
                employee = Employee.objects.get(employee=user)
                # Deactivate the employee
                user.is_active = False
                user.save()
                return Response({"message": "Employee deactivated successfully."})
            else:
                return Response({"error": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, ParkOwner.DoesNotExist, Customer.DoesNotExist, Employee.DoesNotExist):
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)


# {
#     "user_type": "employee"
# }
