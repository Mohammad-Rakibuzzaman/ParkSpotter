from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Customer(models.Model):
    customer_id = models.OneToOneField(
        User, related_name="customer", on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=12)
    vehicle_brand = models.CharField(max_length=50, null=True, blank=True)
    plate_number = models.CharField(max_length=50, null=True, blank=True)
    joined_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return self.customer_id.username

