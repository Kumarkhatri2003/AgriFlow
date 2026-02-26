from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Crop(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops')

    name = models.CharField(max_length=255)
    name_np = models.CharField(max_length=255,blank=True)
    variety = models.CharField(max_length=255, blank=True)

    field_name = models.CharField(max_length=255)

    AREA_UNITS = [
        ('ropani', 'Ropani'),
        ('kattha', 'Kattha'),
        ('bigha', 'Bigha'),
        ('hectare', 'Hectare'),
    ]

    field_area = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit = models.CharField(max_length=50,choices=AREA_UNITS, default='ropani')

    planting_date = models.DateField()
    expected_harvest_date = models.DateField(null=True, blank=True) 

    GROWTH_STAGES =[
        ('seeding', 'Seeding'),
        ('vegetative', 'Vegetative'),
        ('flowering', 'Flowering'),
        ('fruiting', 'Fruiting'),
        ('harvest', 'Harvest'),
    ]

    growth_stage =models.CharField(max_length=50, choices=GROWTH_STAGES, default='seeding')

    IRRIGATION_TYPES =[
        ('rainfed', 'Rainfed'),
        ('irrigated', 'Irrigated'),
        ('drip', 'Drip'),
        ('sprinkler', 'Sprinkler'),
    ]

    irrigation_type = models.CharField(max_length=50, choices=IRRIGATION_TYPES,default='rainfed')

    soil_type = models.CharField(max_length=100, blank=True)

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('harvested', 'Harvested'),
        ('done', 'Done'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name}- {self.field_name}"

   
    


