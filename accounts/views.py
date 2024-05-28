from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Sum
#12-5 added by rtz
from .serializers import SlotSerializer, ZoneSerializer, BookingSerializer, VehicleSerializer, SubscriptionSerializer, SalarySerializer, SalaryPaymentSerializer, BookingSummarySerializer, ZoneSummarySerializer, EmployeeSerializer
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
from .models import ParkOwner, Slot, Zone, Booking, Vehicle, Subscription, Employee, Salary
from customer.models import Customer
from django.db.models import Q
from datetime import datetime

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
            salary.is_paid = True
            salary.payment_date = timezone.now()
            salary.effective_from = serializer.validated_data.get(
                'effective_from')
            salary.effective_to = serializer.validated_data.get('effective_to')
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
        user.is_staff = True
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

                if is_park_owner:
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
class ZoneAPIView(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

    # permission_classes = [IsAuthenticated]

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

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


def nearby_parking_lots(request):
    park_owners = ParkOwner.objects.all()
    return render(request, 'nearby_parking_lots.html', {
        'park_owners': park_owners,
    })


# class ParkOwnerDashboardViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]

#     def list(self, request):
#         user = request.user
#         try:
#             park_owner = ParkOwner.objects.get(park_owner_id=user)
#         except ParkOwner.DoesNotExist:
#             return Response({"error": "You are not a ParkOwner."}, status=status.HTTP_403_FORBIDDEN)

#         # Get booking summary
#         bookings = Booking.objects.filter(zone__park_owner=park_owner)
#         booking_serializer = BookingSummarySerializer(bookings, many=True)

#         # Get zone summary
#         zones = Zone.objects.filter(park_owner=park_owner)
#         zone_serializer = ZoneSummarySerializer(zones, many=True)

#         employees = Employee.objects.filter(park_owner_id=park_owner)
#         employee_serializer = EmployeeSerializer(employees, many=True)

#         salaries = Salary.objects.filter(employee__in=employees)
#         salary_serializer = SalarySerializer(salaries, many=True)

#         # Total earnings
#         total_earnings = sum(booking.total_amount for booking in bookings)
#         total_salary_cost = sum(salary.amount for salary in salaries)
#         net_revenue = total_earnings - total_salary_cost
#         # Total bookings
#         total_bookings = bookings.count()
#         total_employees = employees.count()

#         dashboard_data = {
#             "total_earnings": total_earnings,
#             "total_bookings": total_bookings,
#             "employees": employee_serializer.data,
#             "bookings": booking_serializer.data,
#             "zones": zone_serializer.data,
#             "total_salary_cost": total_salary_cost,
#             "net_revenue": net_revenue,
#             "total_employees":total_employees,
#         }

#         return Response(dashboard_data)


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
                booking_date__date__gte=start_date,
                booking_date__date__lte=end_date
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
        # Total bookings
        total_bookings = bookings.count()
        total_employees = employees.count()

        dashboard_data = {
            "total_earnings": total_earnings,
            "total_bookings": total_bookings,
            "employees": employee_serializer.data,
            "bookings": booking_serializer.data,
            "zones": zone_serializer.data,
            "total_salary_cost": total_salary_cost,
            "net_revenue": net_revenue,
            "total_employees": total_employees,
        }

        return Response(dashboard_data)
