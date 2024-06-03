from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter() 

router.register('parkowner-list', views.ParkownerProfileViewset)
router.register('employee-list', views.EmployeeProfileViewset)
router.register('zone', views.ZoneViewSet, basename='zone')
router.register('slot', views.SlotAPIView, basename='slot')
router.register('salary', views.SalaryViewSet, basename='salary')
router.register('bookings', views.BookingViewSet, basename='booking')
router.register(
    'subscription_package', views.SubscriptionPackageViewSet, basename='subscription_package')
router.register(
    'subscription', views.SubscriptionViewSet, basename='subscription')
router.register('park_owner_dashboard',
                views.ParkOwnerDashboardViewSet, basename='park_owner_dashboard')
router.register('admin_dashboard',
                views.AdminDashboardViewSet, basename='admin_dashboard')
urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('employee-register/', views.EmployeeRegistrationView.as_view(), name='employee-register'),
    path('user_login/', views.UserLoginApiView.as_view(), name='user_login'),
    path('active/<uid64>/<token>/', views.activate, name = 'activate'),
    path('profile/<int:park_owner_id__id>/', views.ParkownerProfileUpdateView.as_view(), name='parkowner-profile-update'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('nearby-parking-lots/', views.nearby_parking_lots, name='nearby_parking_lots'),
    #added rtz 12/5
    # path('zone/', views.ZoneAPIView.as_view(), name='zone'),
    # path('bookings/', views.BookingCreateAPIView.as_view(), name='booking'),
]