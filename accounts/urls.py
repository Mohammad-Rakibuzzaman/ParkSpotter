from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter() 

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('user_login/', views.UserLoginApiView.as_view(), name='user_login'),
    path('active/<uid64>/<token>/', views.activate, name = 'activate'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    #added rtz 12/5
    path('park_details/', views.ParkDetailListView.as_view(), name='park_detail_list'),
    path('booking/', views.BookingListView.as_view(), name='booking'),
]