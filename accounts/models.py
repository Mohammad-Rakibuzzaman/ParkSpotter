from django.db import models
from django.contrib.auth.models import User
import math

from customer.models import Customer
from .constants import TIME_SLOT,PACKAGE
from datetime import timedelta, date
from django.db.models import Sum
from decimal import Decimal

# Create your models here.


class SubscriptionPackage(models.Model):
    name = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False,null=True,blank=True)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Calculate amount
        self.amount = self.price
        # Calculate total_amount
        discount_amount = (self.discount / 100) * self.price
        self.total_amount = self.price - discount_amount

        super().save(*args, **kwargs)

    @property
    def duration_days(self):
        return self.duration_months * 31
    
# class Subscription(models.Model):
#     package = models.ForeignKey(SubscriptionPackage, on_delete=models.CASCADE,null=True,blank=True)
#     start_date = models.DateField(auto_now_add=True)
#     end_date = models.DateField(null=True, blank=True)
    
#     def save(self, *args, **kwargs):
#         if not self.pk:
#             self.end_date = date.today() + timedelta(days=self.package.duration_days)
#         else:
#             existing = Subscription.objects.get(pk=self.pk)
#             if existing.end_date > date.today():
#                 remaining_days = (existing.end_date - date.today()).days
#                 self.end_date = date.today() + timedelta(days=remaining_days + self.package.duration_days)
#             else:
#                 self.end_date = date.today() + timedelta(days=self.package.duration_days)

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.package.name}"

class ParkOwner(models.Model):
    park_owner_id = models.OneToOneField(
        User, related_name="owner", on_delete=models.CASCADE)
    subscription_id = models.ForeignKey(
        SubscriptionPackage, related_name="subscription", on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(
        upload_to='media/owner_images/', blank=True, null=True)
    mobile_no = models.CharField(max_length=11)
    nid_card_no = models.CharField(max_length=11)
    slot_size = models.CharField(max_length=200)
    capacity = models.CharField(max_length=200,default=0)
    address = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(auto_now_add=True, null=True, blank=True)
    joined_date = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True)
    available_slot = models.PositiveIntegerField(default=0)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.subscription_id:
            self.subscription_start_date = None
            self.subscription_end_date = None
        else:
            if not self.subscription_start_date:
                self.subscription_start_date = date.today()
            self.subscription_end_date = self.subscription_start_date + \
                timedelta(days=self.subscription_id.duration_days)
        super().save(*args, **kwargs)

    def update_capacity(self):
        total_capacity = self.park_zones.aggregate(
            total=Sum('capacity'))['total'] or 0
        self.capacity = total_capacity
        self.save(update_fields=['capacity'])

    def update_available_slot(self):
        total_available_slots = Slot.objects.filter(
            zone__park_owner=self, available=True).count()
        self.available_slot = total_available_slots
        self.save(update_fields=['available_slot'])

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
    
    def __str__(self):
        return self.employee.username


class Salary(models.Model):
    employee = models.ForeignKey(
        Employee, related_name="salaries", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Employee: {self.employee.employee.username}"

class Zone(models.Model):
    park_owner = models.ForeignKey(
        ParkOwner, related_name="park_zones", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure slots are created
        for slot_number in range(1, self.capacity + 1):
            Slot.objects.get_or_create(zone=self, slot_number=slot_number)
        self.park_owner.update_capacity()

    def delete(self, *args, **kwargs):
        park_owner = self.park_owner
        super().delete(*args, **kwargs)
        park_owner.update_capacity()

    def __str__(self):
        return f"Zone {self.name}"


class Slot(models.Model):
    zone = models.ForeignKey(
        Zone, related_name='slots', on_delete=models.CASCADE,null=True)
    slot_number = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        updating = self.pk is not None
        previous_slot = None
        if updating:
            previous_slot = Slot.objects.get(pk=self.pk)
        super().save(*args, **kwargs)
        if not updating or (updating and previous_slot.available != self.available):
            self.zone.park_owner.update_available_slot()

    def __str__(self):
        return f"Slot {self.slot_number} for {self.zone}"

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=12)


class Booking (models.Model):
    employee= models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True)
    customer= models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.ForeignKey(
        Slot, on_delete=models.CASCADE, null=True, blank=True)
    fine = models.IntegerField(default=0, null=True, blank=True)
    status = models.BooleanField(default=False)
    rate_per_minute = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0.50'))
    booking_time = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    check_in_time = models.DateTimeField(blank=True, null=True)
    appoximate_check_out_time = models.DateTimeField(blank=True, null=True)
    check_out_time = models.DateTimeField(blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    class Meta:
        unique_together = ('slot', 'status')
    

    def save(self, *args, **kwargs):
        # Check if the slot is available before booking
        if Booking.objects.filter(slot=self.slot, check_out_time__isnull=True).exclude(id=self.id).exists():
            raise ValueError("This slot is already booked.")
        
        if self.slot:
            if not self.check_out_time:
                self.slot.available = False
                self.status = True 
                self.is_paid = False
            else:
                self.slot.available = True
                self.status = False  
                self.is_paid = True
                
            self.slot.save()

        if self.check_out_time and self.appoximate_check_out_time:
            self.calculate_fine()

        super().save(*args, **kwargs)
        self.update_customer_points()

    def ticket_no(self):
        zone_name = self.zone.name
        ticket_number = 1000 + self.id
        return f"SP-{zone_name}-{ticket_number}"

    def calculate_booking_amount(self):
        if self.check_in_time is None or self.appoximate_check_out_time is None:
            return Decimal('0.00')
        duration_seconds = Decimal(
            (self.appoximate_check_out_time - self.check_in_time).total_seconds())
        duration_minutes = duration_seconds / Decimal(60)
        return round(duration_minutes * self.rate_per_minute, 2)

    @property
    def amount(self):
        return self.calculate_booking_amount()
    
    def calculate_fine(self):
        if self.check_out_time and self.appoximate_check_out_time:
            overtime = self.check_out_time - self.appoximate_check_out_time
            if overtime > timedelta(0):
                overtime_minutes = overtime.total_seconds() / 60
                self.fine = 20 + round(overtime_minutes)

    @property
    def total_amount(self):
        return self.amount + (self.fine or Decimal('0.00'))

    def __str__(self):
        return f"Booking for {self.vehicle} ({self.check_in_time} - {self.appoximate_check_out_time})"
    
    def update_customer_points(self):
        if self.customer:
            duration_hours = (self.appoximate_check_out_time - self.check_in_time).total_seconds() / 3600
            points = int(duration_hours)
            
            if self.fine > 0:
                points -= 1
            
            self.customer.points += points
            self.customer.save(update_fields=['points'])

