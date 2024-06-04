from django.shortcuts import render
from .serializers import CustomerRegistrationSerializer,CustomerSerializer
from rest_framework import generics
from .models import Customer
from rest_framework import viewsets,status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from accounts.models import Booking
from .models import Customer
from accounts.serializers import BookingSerializer
# Create your views here.


class CustomerListViewset(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerRegistrationView(generics.CreateAPIView):
    serializer_class = CustomerRegistrationSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        customer = serializer.save()
        customer.is_active = True
        customer.save()


class CustomerDashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        try:
            customer = Customer.objects.get(customer_id=user)
        except Customer.DoesNotExist:
            return Response({"error": "You are not a Customer."}, status=status.HTTP_403_FORBIDDEN)

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
        bookings = Booking.objects.filter(customer=customer)
        if start_date and end_date:
            bookings = bookings.filter(
                booking_time__date__gte=start_date,
                booking_time__date__lte=end_date
            )

        booking_serializer = BookingSerializer(bookings, many=True)
        customer_serializer = CustomerSerializer(customer)

        dashboard_data = {
            "customer": customer_serializer.data,
            "bookings": booking_serializer.data
        }

        return Response(dashboard_data)
