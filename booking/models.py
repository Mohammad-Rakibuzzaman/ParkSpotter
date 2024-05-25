from django.db import models

# Create your models here.


# class Meta:
#         unique_together = ('slot', 'status')

#     def find_next_available_slot(self):
#         if not self.zone:
#             return None

#         booked_slots = Booking.objects.filter(
#             zone=self.zone, status=True).values_list('slot_id', flat=True)
#         booked_slots = list(booked_slots)

#         available_slots = Slot.objects.filter(
#             zone=self.zone, available=False).exclude(id__in=booked_slots)
#         if available_slots.exists():
#             return available_slots.first()
#         return None

#     def save(self, *args, **kwargs):
#         # If it's an update, handle the old slot availability
#         if self.pk:
#             old_booking = Booking.objects.get(pk=self.pk)
#             if old_booking.slot and old_booking.slot != self.slot:
#                 old_booking.slot.available = False
#                 old_booking.slot.save()

#         # Assign the slot if not already assigned
#         if self.slot is None:
#             self.slot = self.find_next_available_slot()
#             if self.slot is None:
#                 raise ValueError("No available slots in the selected zone.")

#         # Check if the selected slot is already booked
#         if Booking.objects.filter(slot=self.slot, status=True).exists():
#             raise ValueError("This slot is already booked.")

#         # Mark the slot as available
#         self.slot.available = True
#         self.slot.save()

#         super().save(*args, **kwargs)

#     def delete(self, *args, **kwargs):
#         # Mark the slot as unavailable when the booking is deleted
#         if self.slot:
#             self.slot.available = False
#             self.slot.save()
#         super().delete(*args, **kwargs)