from django.contrib import admin
from .models import (
    Crop, FertilizerRecord, PesticideRecord,
    CropExpense, CropIncome, HarvestRecord
)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    # Columns shown in Django admin table
    list_display = ['name', 'field_name', 'farmer', 'status', 'planting_date', 'growth_stage']

    # Filters shown on right side
    list_filter = ['status', 'area_unit', 'growth_stage', 'is_irrigated']

    # Search box fields
    search_fields = ['name', 'name_np', 'field_name', 'farmer__username']


@admin.register(FertilizerRecord)
class FertilizerRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop', 'fertilizer_type', 'quantity', 'unit', 'cost', 'application_date']
    list_filter = ['fertilizer_type', 'application_date']
    search_fields = ['name', 'crop__name']


@admin.register(PesticideRecord)
class PesticideRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_pest', 'crop', 'quantity', 'unit', 'cost', 'application_date']
    list_filter = ['application_date']
    search_fields = ['name', 'target_pest', 'crop__name']


@admin.register(CropExpense)
class CropExpenseAdmin(admin.ModelAdmin):
    list_display = ['crop', 'category', 'amount', 'date', 'description']
    list_filter = ['category', 'date']
    search_fields = ['description', 'crop__name', 'vendor_name']


@admin.register(CropIncome)
class CropIncomeAdmin(admin.ModelAdmin):
    list_display = ['crop', 'source', 'amount', 'date', 'description', 'buyer_name']
    list_filter = ['source', 'date']
    search_fields = ['description', 'crop__name', 'buyer_name']


@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ['crop', 'harvest_date', 'quantity', 'unit', 'quality']
    list_filter = ['quality', 'harvest_date']
    search_fields = ['crop__name', 'notes']