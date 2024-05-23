from django.shortcuts import render
from .serializers import CustomerRegistrationSerializer,CustomerSerializer
from rest_framework import generics
from .models import Customer
from rest_framework import viewsets
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

