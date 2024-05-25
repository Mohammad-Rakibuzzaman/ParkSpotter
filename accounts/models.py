from django.db import models
from django.contrib.auth.models import User
import math
from .constants import TIME_SLOT,PACKAGE
from datetime import timedelta, date
from django.db.models import Sum
from decimal import Decimal

# Create your models here.

class Subscription(models.Model):
    package = models.IntegerField(choices=PACKAGE, default=1)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    @property
    def amount(self):
        if self.package == 1:
            return 1000
        elif self.package == 2:
            return 5000
        elif self.package == 3:
            return 10000
        else:
            return 0

    def save(self, *args, **kwargs):
        if self.package == 1:
            duration = timedelta(days=30)
        elif self.package == 2:
            duration = timedelta(days=182)
        elif self.package == 3:
            duration = timedelta(days=365)
        else:
            raise ValueError("Invalid package type")

        if self.pk is not None:
            existing = Subscription.objects.get(pk=self.pk)
            if existing.end_date > date.today():
                remaining_days = (existing.end_date - date.today()).days
                duration += timedelta(days=remaining_days)

        self.end_date = date.today() + duration

        super().save(*args, **kwargs)

    def __str__(self):
        return f"({self.get_package_display()})"


class ParkOwner(models.Model):
    park_owner_id = models.OneToOneField(
        User, related_name="owner", on_delete=models.CASCADE)
    subscription_id = models.ForeignKey(
        Subscription, related_name="subscription", on_delete=models.CASCADE, null=True)
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
    
    def update_capacity(self):
        total_capacity = self.park_zones.aggregate(
            total=Sum('capacity'))['total'] or 0
        self.capacity = total_capacity
        self.save(update_fields=['capacity'])

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

    def __str__(self):
        return f"Slot {self.slot_number} for {self.zone}"

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)
    mobile_no = models.CharField(max_length=12)


class Booking (models.Model):
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

    class Meta:
        unique_together = ('slot', 'status')

    def save(self, *args, **kwargs):
        # Check if the slot is available before booking
        if self.slot and not self.slot.available:
            raise ValueError("This slot is already booked.")

        # Ensure that the slot is marked as unavailable upon booking
        if self.slot:
            self.slot.available = False
            self.slot.save()
        
        if self.check_out_time and self.appoximate_check_out_time:
            self.calculate_fine()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Optionally, mark the slot as available when the booking is deleted
        if self.slot:
            self.slot.available = True
            self.slot.save()
        super().delete(*args, **kwargs)
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
    

