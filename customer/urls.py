from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views
router = DefaultRouter()

router.register('customer-list', views.CustomerListViewset)
router.register('customer_dashboard', views.CustomerDashboardViewSet,
                basename='customer_dashboard')

urlpatterns = [
    path('', include(router.urls)),
    path('customer_register/', views.CustomerRegistrationView.as_view(),
         name='customer_register'),

]

