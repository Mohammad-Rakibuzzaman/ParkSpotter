from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ParkOwner(models.Model):
    user = models.OneToOneField(User, related_name="owner", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/owner_images/', blank=True, null=True)
    mobile_no = models.CharField(max_length=11)
    email=models.EmailField()
    nid_card_no = models.CharField(max_length=11)
    slot_size = models.CharField(max_length=200)
    capacity = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=200)
    card_no = models.CharField(max_length=50)
    amount=models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)      
    joined_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.user.username
