from django.contrib import admin
from .models import Crop


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    # Columns shown in Django admin table
    list_display = ['name', 'field_name', 'farmer', 'status', 'planting_date']

    # Filters shown on right side
    list_filter = ['status', 'area_unit', 'growth_stage', 'irrigation_type']

    # Search box fields
    search_fields = ['name', 'name_np', 'field_name', 'farmer__username']