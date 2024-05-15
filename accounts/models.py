from django.db import models
from django.contrib.auth.models import User
import math
from .constants import TIME_SLOT

# Create your models here.

PARK_PLAN = []


class ParkOwner(models.Model):
    park_owner_id = models.OneToOneField(
        User, related_name="owner", on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='media/owner_images/', blank=True, null=True)
    mobile_no = models.CharField(max_length=11)
    email = models.EmailField()
    nid_card_no = models.CharField(max_length=11)
    slot_size = models.CharField(max_length=200)
    zone = models.PositiveIntegerField(default=1)
    capacity = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True, null=True, blank=True)
    joined_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):

        global PARK_PLAN
        PARK_PLAN.clear()
        for slot_number in range(1, int(self.capacity) + 1):
            PARK_PLAN.append((str(slot_number), str(slot_number)))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.park_owner_id.username


class Employee(models.Model):
    park_owner_id = models.ForeignKey(
        ParkOwner, related_name="employees_owner", on_delete=models.CASCADE, blank=True, null=True)
    employee = models.OneToOneField(
        User, related_name="employee_profile", on_delete=models.CASCADE,null=True)
    mobile_no = models.CharField(max_length=12)
    qualification = models.CharField(max_length=50, null=True, blank=True)
    nid_card_no = models.CharField(max_length=11)
    address = models.CharField(max_length=200, blank=True, null=True)
    joined_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)


class Zone(models.Model):
    park_owner_id = models.ForeignKey(
        ParkOwner, related_name="park_zone", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Zone {self.name}"


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=12)


#subscription model added 16-5
class Subscription(models.Model):
    package = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    user = models.ForeignKey(User, related_name='subscriptions', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.package} Subscription for {self.user}"





class Booking (models.Model):
    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.IntegerField(choices=PARK_PLAN, default=1)
    fine = models.IntegerField(default=0, null=True, blank=True)
    time_slot = models.IntegerField(choices=TIME_SLOT)
    status = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    #new added from subscription model
    subscription = models.ForeignKey(Subscription, related_name='bookings', on_delete=models.CASCADE, null=True, blank=True)




    def ticket_no(self):

        zone_name = self.zone.name
        ticket_number = 1000 + self.id
        return f"SP-{zone_name}-{ticket_number}"

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
    


    



