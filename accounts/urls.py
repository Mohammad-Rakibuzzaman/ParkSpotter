from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter() 

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationApiView.as_view(), name='register'),
    path('user_login/', views.UserLoginApiView.as_view(), name='user_login'),
    path('active/<uid64>/<token>/', views.activate, name = 'activate'),
]