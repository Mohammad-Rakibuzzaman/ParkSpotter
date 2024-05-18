from django.shortcuts import render
from rest_framework import viewsets
from . import models
from . import serializers
#12-5 added by rtz
from .serializers import ZoneSerializer, BookingSerializer, VehicleSerializer, SubscriptionSerializer
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
from .models import ParkOwner, Zone, Booking, Vehicle, Subscription,Employee


# Create your views here.
class ParkownerProfileViewset(viewsets.ModelViewSet):
    queryset = ParkOwner.objects.all()
    serializer_class = serializers.ParkownerSerializer


class EmployeeProfileViewset(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class ParkownerProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = models.ParkOwner.objects.all()
    serializer_class = serializers.ParkownerSerializer
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
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
class UserLoginApiView(APIView):
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                try:
                    park_owner = ParkOwner.objects.get(park_owner_id =user)
                except ParkOwner.DoesNotExist:
                    return Response(
                        {"detail": "User is not a park owner."},                        status=status.HTTP_403_FORBIDDEN
                    )
                token, _ = Token.objects.get_or_create(user=user)

                login(request, user)
                is_staff = user.is_staff
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'is_staff': is_staff
                })

            else:
                
                return Response({'error': "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')
    
#12.5 rtzaddedd
class ZoneAPIView(APIView):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer

    # permission_classes = [IsAuthenticated]
    

class BookingCreateAPIView(APIView):
    
    def post(self, request, format=None):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionListCreateView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
