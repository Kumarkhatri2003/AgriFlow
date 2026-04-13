from django.contrib import admin
from .models import (
    Crop, CropRecommendationHistory, FertilizerRecord, PesticideRecord,
    CropExpense, CropIncome, HarvestRecord, CropKnowledgeBase, Labour
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


@admin.register(CropKnowledgeBase)
class CropKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'category', 'best_season', 'water_req', 'drought_tolerance']
    list_filter = ['category', 'best_season', 'water_req', 'frost_sensitive']
    search_fields = ['name_en', 'name_np']
    fieldsets = (
        ('Basic', {'fields': ('name_en', 'name_np', 'category')}),
        ('Season', {'fields': ('best_season', 'other_seasons')}),
        ('Temperature', {'fields': ('temp_min', 'temp_max', 'temp_ideal')}),
        ('Soil & pH', {'fields': ('soil_ideal', 'soil_other', 'ph_min', 'ph_max', 'ph_ideal')}),
        ('Water & Region', {'fields': ('water_req', 'region_suitable')}),
        ('Tolerances', {'fields': ('drought_tolerance', 'frost_sensitive')}),
        ('Labor & Storage', {'fields': ('labor_req', 'storage_life')}),
        ('NPK Needs', {'fields': ('n_need', 'p_need', 'k_need')}),
    )


@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop', 'workers_count', 'days', 'rate_per_day', 'total_cost', 'date']
    list_filter = ['date']
    search_fields = ['name', 'crop__name', 'notes']
    readonly_fields = ['total_cost']  # Make total_cost read-only since it's auto-calculated
    
    
@admin.register(CropRecommendationHistory)
class CropRecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'season', 'region', 'created_at']
    list_filter = ['season', 'region', 'created_at']
    search_fields = ['farmer__username']
    readonly_fields = ['recommendations']  # Make JSON field read-only