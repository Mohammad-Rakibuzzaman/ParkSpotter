from django.db import models
from django.contrib.auth.models import User
import math
from .constants import TIME_SLOT, PARK_PLAN

# Create your models here.


class ParkOwner(models.Model):
    park_owner_id = models.OneToOneField(User, related_name="owner", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/owner_images/', blank=True, null=True)
    mobile_no = models.CharField(max_length=11)
    email=models.EmailField()
    nid_card_no = models.CharField(max_length=11)
    slot_size = models.CharField(max_length=200)
    capacity = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200,null=True, blank=True)
    amount=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True, null=True, blank=True)      
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.park_owner_id.username

class Employee(models.Model):
    name = models.CharField(max_length=50)
    mobile_no = models.CharField(max_length=12)
    qualification = models.CharField(max_length=50, null=True, blank=True)
    nid_card_no = models.CharField(max_length=11)
    address = models.CharField(max_length=200, blank=True, null=True)
    joined_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)


class Park_Detail(models.Model):
    park_owner = models.ForeignKey(
        ParkOwner, related_name="park_details", on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Park Detail for {self.park_owner.id}"

    # def save(self, *args, **kwargs):
    #     # Generate the park_plan_text before saving
    #     self.park_plan_text = self.generate_park_plan_text()
    #     super(Park_Detail, self).save(*args, **kwargs)

    # def generate_park_plan_text(self):
    #     park_plan_text = ""

    #     for i in range(1, self.capacity + 1):
    #         park_plan_text += f"(1,{i}) "

    #     return park_plan_text.strip()


class Vehicle(models.Model):
    plate_number=models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=12)

PARK_PLAN=[
    ('1','1'),
    ('2','2'),
    ('3','3'),
    ('4','4'),
    ('5','5'),
    ('6','6'),
    ('7','7'),
    ('8','8'),
    ('9','9'),
    ('10','10')
]
class Booking (models.Model):
    park_detail=models.ForeignKey(Park_Detail, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.IntegerField(choices=PARK_PLAN,default=1)
    fine=models.IntegerField(default=0,null=True,blank=True)
    time_slot = models.IntegerField(choices=TIME_SLOT)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)

    @property
    def amount(self):
        if self.time_slot == '1':
            return 30
        elif self.time_slot == '2':
            return 50
        elif self.time_slot == '3':
            return 100
        else:
            return 0 

    def __str__(self):
        return f"Booking for {self.vehicle} ({self.get_time_slot_display()})"
