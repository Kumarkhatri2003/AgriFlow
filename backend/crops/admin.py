from django.contrib import admin
from .models import Crop,FertilizerRecord,PesticideRecord


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    # Columns shown in Django admin table
    list_display = ['name', 'field_name', 'farmer', 'status', 'planting_date']

    # Filters shown on right side
    list_filter = ['status', 'area_unit', 'growth_stage', 'irrigation_type']

    # Search box fields
    search_fields = ['name', 'name_np', 'field_name', 'farmer__username']
    
@admin.register(FertilizerRecord)
class FertilizerRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop', 'quantity', 'unit', 'application_date']
    list_filter = ['fertilizer_type', 'application_date']
    

@admin.register(PesticideRecord)
class PesticideRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_pest', 'crop', 'application_date']
    list_filter = ['application_date']