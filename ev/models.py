from django.db import models

# Create your models here.
class Charger(models.Model):
    CHARGER_TYPES = [
        ('AC', 'AC Charger'),
        ('DC', 'DC Fast Charger'),
    ]
class EvStation(models.Model):
    name = models.CharField(max_length=255)  # ✅ Added max_length
    address = models.CharField(max_length=255)  # ✅ Added max_length
    city = models.CharField(max_length=100)  # ✅ Added max_length
    state = models.CharField(max_length=100)  # ✅ Added max_length
    zip_code = models.CharField(max_length=20)  # ✅ Added max_length
    is_available = models.BooleanField(default=True)  # ✅ Default value set
    gps_location = models.CharField(max_length=100, null=True, blank=True)  # ✅ Added max_length, null, and blank

    def __str__(self):
        return f"{self.name} - {self.city}, {self.state}"