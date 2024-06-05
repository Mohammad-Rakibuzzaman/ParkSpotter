from django.contrib import admin
from . import models
# Register your models here.
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','mobile_no']
    
    def first_name(self,obj):
        return obj.park_owner_id.first_name
    
    def last_name(self,obj):
        return obj.park_owner_id.last_name
    def save_model(self, request, obj, form, change):
        
        if not obj.park_owner_id_id:
            user = models.User.objects.get(pk=request.POST.get('park_owner_id'))
            obj.park_owner_id = user
        super().save_model(request, obj, form, change)
    
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','mobile_no']
    
    def first_name(self,obj):
        return obj.employee.first_name
    
    def last_name(self,obj):
        return obj.employee.last_name
    def save_model(self, request, obj, form, change):
        
        if not obj.employee_id:
            user = models.User.objects.get(pk=request.POST.get('employee'))
            obj.employee = user
        super().save_model(request, obj, form, change)


class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'created_at')
    
admin.site.register(models.ParkOwner, UserProfileAdmin)
admin.site.register(models.Zone,ZoneAdmin)
admin.site.register(models.Booking)
admin.site.register(models.Vehicle)
admin.site.register(models.Employee,EmployeeProfileAdmin)
# admin.site.register(models.Subscription)
admin.site.register(models.SubscriptionPackage)
admin.site.register(models.Slot)
admin.site.register(models.Salary)
