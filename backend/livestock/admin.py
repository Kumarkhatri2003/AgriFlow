from django.contrib import admin
from .models import AnimalType,Animal
# Register your models here.


@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display=['name','name_np','gestation_days','is_milk_animal','is_egg_animal']
    
    list_filter = ['is_milk_animal','is_egg_animal']
    
    search_fields = ['name', 'name_np']
    
    
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display =['tag_number','name','animal_type','farmer','gender','status']
    list_filter = ['animal_type','gender','status', 'is_pregnant']
    search_fields =['tag_number','name','farmer_email']
    readonly_fields = ['created_at','updated_at']
