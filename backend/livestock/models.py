from django.db import models
from django.contrib.auth import get_user_model
import uuid


User = get_user_model()
# Create your models here.

class AnimalType(models.Model):
    """Master list of animal types (Cow, Goat, Chicken,etc)"""
    
    name = models.CharField(max_length=100)
    name_np = models.CharField(max_length=100, blank=True)
    
    
    avg_lifespan_years = models.DecimalField(max_digits=4,decimal_places=1,null=True, blank=True)
    gestation_days = models.IntegerField(null=True,blank=True)
    
    is_milk_animal = models.BooleanField(default=False)
    is_egg_animal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    
    
class Animal(models.Model):
    """Individual animal owned by a farmer"""
    
    id = models.UUIDField(primary_key= True, default=uuid.uuid4,editable=False)
    farmer = models.ForeignKey(User,on_delete=models.CASCADE,related_name='animals')
    
    #basic info
    animal_type = models.ForeignKey(AnimalType,on_delete=models.PROTECT, related_name='animals')
    name = models.CharField(max_length=100,blank=True)
    tag_number = models.CharField(max_length=50,unique=True)
    
    
    #birth or acquisition info
    birth_date = models.DateField(null=True,blank=True)
    acquisition_date = models.DateField()
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    
    
    GENDER_CHOICES = [
        ('male','Male'),
        ('female','Female'),
        ('unknown','Unknown'),
    ]
    
    gender = models.CharField(max_length=20,choices=GENDER_CHOICES,default='unknown')
    
    
    #current status 
    STATUS_CHOICES = [
        ('active','Active'),
        ('sold','Sold'),
        ('dead','Dead'),
        ('butchered','Butchered'),
    ]
    
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='active')
    
    
    #Health and breading
    is_pregnant = models.BooleanField(default=False)
    last_pregnancy_date= models.DateField(null=True,blank=True)
    expected_birth_date = models.DateField(null=True,blank=True)
    
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        if self.name:
            return f"{self.animal_type}-{self.name}({self.tag_number})"
        
        return f"{self.animal_type}-{self.tag_number}"
    

class VaccinationRecord(models.Model):
    """Track vaccinations given to animals"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vaccinations')
    
    vaccine_name = models.CharField(max_length=255)
    vaccine_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    
    administered_by = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-vaccine_date']
    
    def __str__(self):
        return f"{self.vaccine_name} - {self.animal} on {self.vaccine_date}"


class HealthRecord(models.Model):
    """Track health issues, treatments, checkups"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    
    HEALTH_TYPES = [
        ('checkup', 'Regular Checkup'),
        ('sick', 'Sickness'),
        ('injury', 'Injury'),
        ('treatment', 'Treatment'),
        ('other', 'Other'),
    ]
    health_type = models.CharField(max_length=20, choices=HEALTH_TYPES, default='checkup')
    
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField(blank=True)
    treatment_date = models.DateField()
    follow_up_date = models.DateField(null=True, blank=True)
    
    vet_name = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-treatment_date']
    
    def __str__(self):
        return f"{self.get_health_type_display()} - {self.animal} on {self.treatment_date}"


    