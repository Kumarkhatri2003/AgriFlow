from django.contrib import admin
from .models import (
    Crop, CropRecommendationHistory, FertilizerRecord, PesticideRecord,
    CropExpense, CropIncome, HarvestRecord, CropKnowledgeBase, Labour,
    CropTypeConfig, CropActivityRule,
)


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'field_name', 'farmer', 'status', 'planting_date', 'growth_stage']
    list_filter = ['status', 'area_unit', 'growth_stage', 'is_irrigated']
    search_fields = ['name', 'name_np', 'field_name', 'farmer__username']
    list_editable = ['status', 'growth_stage']  # Make editable inline
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'name_np', 'variety', 'farmer')
        }),
        ('Field Information', {
            'fields': ('field_name', 'field_area', 'area_unit', 'soil_type')
        }),
        ('Dates', {
            'fields': ('planting_date', 'expected_harvest_date')
        }),
        ('Growth & Status', {
            'fields': ('growth_stage', 'status', 'is_irrigated', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FertilizerRecord)
class FertilizerRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop', 'fertilizer_type', 'quantity', 'unit', 'cost', 'application_date']
    list_filter = ['fertilizer_type', 'application_date', 'crop']
    search_fields = ['name', 'crop__name', 'notes']
    list_editable = ['quantity', 'unit', 'cost', 'application_date']  # Make editable inline
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Record Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Fertilizer Details', {
            'fields': ('fertilizer_type', 'name', 'quantity', 'unit', 'cost')
        }),
        ('Application', {
            'fields': ('application_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PesticideRecord)
class PesticideRecordAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_pest', 'crop', 'quantity', 'unit', 'cost', 'application_date']
    list_filter = ['application_date', 'crop']
    search_fields = ['name', 'target_pest', 'crop__name', 'notes']
    list_editable = ['quantity', 'unit', 'cost', 'application_date']  # Make editable inline
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Record Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Pesticide Details', {
            'fields': ('name', 'target_pest', 'quantity', 'unit', 'cost')
        }),
        ('Application', {
            'fields': ('application_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropExpense)
class CropExpenseAdmin(admin.ModelAdmin):
    list_display = ['crop', 'category', 'amount', 'date', 'description', 'vendor_name']
    list_filter = ['category', 'date', 'crop']
    search_fields = ['description', 'crop__name', 'vendor_name', 'vendor_contact']
    list_editable = ['amount', 'date', 'category']  # Make editable inline
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Expense Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Expense Details', {
            'fields': ('category', 'amount', 'date', 'description')
        }),
        ('Vendor Information', {
            'fields': ('vendor_name', 'vendor_contact'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropIncome)
class CropIncomeAdmin(admin.ModelAdmin):
    list_display = ['crop', 'source', 'amount', 'date', 'description', 'buyer_name']
    list_filter = ['source', 'date', 'crop']
    search_fields = ['description', 'crop__name', 'buyer_name', 'buyer_contact']
    list_editable = ['amount', 'date', 'source']  # Make editable inline
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Income Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Income Details', {
            'fields': ('source', 'amount', 'date', 'description')
        }),
        ('Buyer Information', {
            'fields': ('buyer_name', 'buyer_contact'),
            'classes': ('collapse',)
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ['crop', 'harvest_date', 'quantity', 'unit', 'quality']
    list_filter = ['quality', 'harvest_date', 'crop']
    search_fields = ['crop__name', 'notes']
    list_editable = ['quantity', 'unit', 'quality', 'harvest_date']  # Make editable inline
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Harvest Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Harvest Details', {
            'fields': ('harvest_date', 'quantity', 'unit', 'quality')
        }),
        ('Additional', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropKnowledgeBase)
class CropKnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ['name_en', 'name_np', 'category', 'best_season', 'water_req', 'drought_tolerance', 'frost_sensitive']
    list_filter = ['category', 'best_season', 'water_req', 'frost_sensitive', 'drought_tolerance']
    search_fields = ['name_en', 'name_np']
    list_editable = ['category', 'best_season', 'water_req', 'drought_tolerance', 'frost_sensitive']  # Make editable inline
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name_en', 'name_np', 'category')
        }),
        ('Season Information', {
            'fields': ('best_season', 'other_seasons')
        }),
        ('Temperature Requirements', {
            'fields': ('temp_min', 'temp_max', 'temp_ideal')
        }),
        ('Soil Requirements', {
            'fields': ('soil_ideal', 'soil_other')
        }),
        ('pH Requirements', {
            'fields': ('ph_min', 'ph_max', 'ph_ideal')
        }),
        ('Water & Region', {
            'fields': ('water_req', 'water_logging_tolerance', 'region_suitable')
        }),
        ('Tolerances', {
            'fields': ('drought_tolerance', 'frost_sensitive')
        }),
        ('Growth Information', {
            'fields': ('growing_days', 'altitude_min', 'altitude_max', 'day_length_sensitive', 'day_length_type')
        }),
        ('Labor & Storage', {
            'fields': ('labor_req', 'storage_life')
        }),
        ('NPK Requirements', {
            'fields': ('n_need', 'p_need', 'k_need')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Labour)
class LabourAdmin(admin.ModelAdmin):
    list_display = ['name', 'crop', 'workers_count', 'days', 'rate_per_day', 'total_cost', 'date']
    list_filter = ['date', 'crop']
    search_fields = ['name', 'crop__name', 'notes']
    list_editable = ['workers_count', 'days', 'rate_per_day', 'date']  # Make editable inline
    readonly_fields = ['id', 'created_at', 'total_cost']  # total_cost is auto-calculated
    
    fieldsets = (
        ('Labor Information', {
            'fields': ('id', 'user', 'crop')
        }),
        ('Worker Details', {
            'fields': ('name', 'workers_count', 'days', 'rate_per_day', 'total_cost')
        }),
        ('Additional', {
            'fields': ('date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropRecommendationHistory)
class CropRecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'season', 'region', 'water_source', 'soil_type', 'created_at']
    list_filter = ['season', 'region', 'water_source', 'soil_type', 'created_at']
    search_fields = ['farmer__username', 'farmer__email']
    readonly_fields = ['farmer', 'recommendations', 'created_at']  # History shouldn't be edited
    
    fieldsets = (
        ('Farmer Information', {
            'fields': ('farmer',)
        }),
        ('Farm Conditions', {
            'fields': ('region', 'season', 'water_source', 'soil_type', 'labor_availability', 'market_distance', 'farming_goal')
        }),
        ('Environmental Data', {
            'fields': ('temperature_override', 'elevation_risk')
        }),
        ('Soil Test Data', {
            'fields': ('ph', 'n', 'p', 'k'),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('recommendations',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CropTypeConfig)
class CropTypeConfigAdmin(admin.ModelAdmin):
    list_display = ['get_display_name', 'crop_name', 'variety', 'region', 'season', 'total_growing_days', 'is_active']
    list_filter = ['crop_name', 'region', 'season', 'is_active']
    search_fields = ['crop_name', 'variety']
    list_editable = ['is_active', 'total_growing_days']  # Make editable inline
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'crop_name', 'variety', 'region', 'season')
        }),
        ('Germination Stage', {
            'fields': (('germination_start_day', 'germination_end_day'),)
        }),
        ('Vegetative Stage', {
            'fields': (('vegetative_start_day', 'vegetative_end_day'),)
        }),
        ('Flowering Stage', {
            'fields': (('flowering_start_day', 'flowering_end_day'),)
        }),
        ('Maturation Stage', {
            'fields': (('maturation_start_day', 'maturation_end_day'),)
        }),
        ('Harvest Stage', {
            'fields': (('harvest_start_day', 'harvest_end_day'),)
        }),
        ('Other Settings', {
            'fields': ('total_growing_days', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = 'Configuration'


@admin.register(CropActivityRule)
class CropActivityRuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'crop_config', 'growth_stage', 'day_offset', 'order', 'is_active']
    list_filter = ['crop_config__crop_name', 'growth_stage', 'is_active']
    search_fields = ['title', 'description', 'title_np', 'description_np']
    list_editable = ['is_active', 'order', 'day_offset']  # Make editable inline
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('id', 'crop_config', 'growth_stage')
        }),
        ('Activity Details (English)', {
            'fields': ('title', 'description')
        }),
        ('Activity Details (Nepali)', {
            'fields': ('title_np', 'description_np'),
            'classes': ('collapse',)
        }),
        ('Optional Information', {
            'fields': ('measurements', 'target_pest', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Timing & Order', {
            'fields': ('day_offset', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )