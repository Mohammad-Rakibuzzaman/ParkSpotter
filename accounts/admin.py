from django.contrib import admin
from . import models
# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','mobile_no']
    
    def first_name(self,obj):
        return obj.park_owner_id.first_name
    
    def last_name(self,obj):
        return obj.park_owner_id.last_name
    
    
admin.site.register(models.ParkOwner, UserProfileAdmin)
admin.site.register(models.Zone)
admin.site.register(models.Booking)
admin.site.register(models.Vehicle)