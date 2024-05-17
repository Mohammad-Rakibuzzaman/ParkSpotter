from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter() 

router.register('parkowner-list', views.ParkownerProfileViewset)
router.register('employee-list', views.EmployeeProfileViewset)
urlpatterns = [
    path('', include(router.urls)),
    path('subscription/', views.SubscriptionListCreateView.as_view(),
         name='subscription'),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('employee-register/', views.EmployeeRegistrationView.as_view(), name='employee-register'),
    path('user_login/', views.UserLoginApiView.as_view(), name='user_login'),
    path('employee_login/', views.EmployeeLoginApiView.as_view(), name='employee_login'),
    path('active/<uid64>/<token>/', views.activate, name = 'activate'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    #added rtz 12/5
    path('zone/', views.ZoneAPIView.as_view(), name='zone'),
    path('bookings/', views.BookingCreateAPIView.as_view(), name='booking'),
]