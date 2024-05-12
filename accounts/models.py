from django.db import models
from django.contrib.auth.models import User
import math

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


class Park_Detail(models.Model):
    park_owner = models.ForeignKey(
        ParkOwner, related_name="park_details", on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(default=5)
    park_plan_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Park Detail for {self.park_owner}"

    def generate_park_plan_text(self):
        rows = int(math.ceil(self.capacity / 5))
        cols = 5

        park_plan_text = ""

        spot_count = 1
        for i in range(rows):
            for j in range(cols):
                if spot_count <= self.capacity:
                    park_plan_text += f"({i+1},{j+1}) "
                    spot_count += 1
                else:
                    break
            park_plan_text += "\n"

        return park_plan_text
