from traceback import format_tb

from django.contrib import admin
from .models import (
    AnimalType, Animal, VaccinationRecord, HealthRecord, 
    MilkRecord, BreedingRecord, AnimalIncome, AnimalExpense
)

# ==================== ANIMAL TYPE ADMIN ====================
@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_np', 'gestation_days', 'is_milk_animal', 'is_egg_animal']
    list_filter = ['is_milk_animal', 'is_egg_animal']
    search_fields = ['name', 'name_np']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_np')
        }),
        ('Animal Characteristics', {
            'fields': ('avg_lifespan_years', 'gestation_days')
        }),
        ('Production Type', {
            'fields': ('is_milk_animal', 'is_egg_animal')
        }),
    )


# ==================== INLINE CLASSES FOR ANIMAL ADMIN ====================
class VaccinationInline(admin.TabularInline):
    """Inline for vaccination records under animal"""
    model = VaccinationRecord
    extra = 0
    fields = ['vaccine_name', 'vaccine_date', 'next_due_date', 'cost']
    readonly_fields = ['created_at']


class HealthInline(admin.TabularInline):
    """Inline for health records under animal"""
    model = HealthRecord
    extra = 0
    fields = ['health_type', 'diagnosis', 'treatment_date', 'cost']
    readonly_fields = ['created_at']


class MilkInline(admin.TabularInline):
    """Inline for milk records under animal"""
    model = MilkRecord
    extra = 0
    fields = ['date', 'quantity_liters', 'milk_time']
    readonly_fields = ['created_at']


class BreedingInline(admin.TabularInline):
    """Inline for breeding records under animal (as mother)"""
    model = BreedingRecord
    fk_name = 'animal'
    extra = 0
    fields = ['breeding_date', 'successful', 'expected_birth_date', 'offspring_count']
    readonly_fields = ['created_at']


class AnimalIncomeInline(admin.TabularInline):
    """Inline for income records under animal"""
    model = AnimalIncome
    extra = 0
    fields = ['source', 'amount', 'date', 'description', 'buyer_name']
    readonly_fields = ['created_at']


class AnimalExpenseInline(admin.TabularInline):
    """Inline for expense records under animal"""
    model = AnimalExpense
    extra = 0
    fields = ['category', 'amount', 'date', 'description', 'vendor_name']
    readonly_fields = ['created_at']


# ==================== ANIMAL ADMIN ====================
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = [
        'tag_number', 'name', 'animal_type', 'farmer', 'gender', 'status', 
        'is_pregnant', 'display_total_income', 'display_total_expense', 'display_net_profit'
    ]
    list_filter = ['animal_type', 'gender', 'status', 'is_pregnant']
    search_fields = ['tag_number', 'name', 'farmer__email', 'farmer__username']
    readonly_fields = ['created_at', 'updated_at', 'display_total_income', 'display_total_expense', 'display_net_profit']
    
    fieldsets = (
        ('Owner Information', {
            'fields': ('farmer',)
        }),
        ('Basic Information', {
            'fields': ('animal_type', 'name', 'tag_number', 'gender')
        }),
        ('Acquisition', {
            'fields': ('birth_date', 'acquisition_date', 'acquisition_cost')
        }),
        ('Status', {
            'fields': ('status', 'is_pregnant', 'last_pregnancy_date', 'expected_birth_date')
        }),
        ('Financial Summary', {
            'fields': ('display_total_income', 'display_total_expense', 'display_net_profit'),
            'classes': ('wide',),
            'description': 'Auto-calculated from related records'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        VaccinationInline, 
        HealthInline, 
        MilkInline, 
        BreedingInline,
        AnimalIncomeInline,
        AnimalExpenseInline
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal_type', 'farmer')
    
    # Custom display methods
    def display_total_income(self, obj):
        return f"NPR {obj.total_income:,.2f}"
    display_total_income.short_description = "Total Income"
    
    def display_total_expense(self, obj):
        return f"NPR {obj.total_expense:,.2f}"
    display_total_expense.short_description = "Total Expense"
    
    def display_net_profit(self, obj):
        profit = obj.net_profit
        color = 'green' if profit >= 0 else 'red'
        return format_tb(
            '<span style="color: {}; font-weight: bold;">NPR {:,.2f}</span>',
            color, profit
        )
    display_net_profit.short_description = "Net Profit"


# ==================== VACCINATION RECORD ADMIN ====================
@admin.register(VaccinationRecord)
class VaccinationRecordAdmin(admin.ModelAdmin):
    list_display = ['vaccine_name', 'animal', 'vaccine_date', 'next_due_date', 'cost']
    list_filter = ['vaccine_date', 'next_due_date']
    search_fields = ['vaccine_name', 'animal__tag_number', 'animal__name']
    date_hierarchy = 'vaccine_date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Animal', {
            'fields': ('animal',)
        }),
        ('Vaccination Details', {
            'fields': ('vaccine_name', 'vaccine_date', 'next_due_date')
        }),
        ('Additional Info', {
            'fields': ('administered_by', 'cost', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== HEALTH RECORD ADMIN ====================
@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'health_type', 'diagnosis', 'treatment_date', 'cost']
    list_filter = ['health_type', 'treatment_date']
    search_fields = ['diagnosis', 'animal__tag_number', 'animal__name']
    date_hierarchy = 'treatment_date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Animal', {
            'fields': ('animal',)
        }),
        ('Health Details', {
            'fields': ('health_type', 'diagnosis', 'treatment', 'treatment_date', 'follow_up_date')
        }),
        ('Additional Info', {
            'fields': ('vet_name', 'cost', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== MILK RECORD ADMIN ====================
@admin.register(MilkRecord)
class MilkRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'date', 'quantity_liters', 'milk_time']
    list_filter = ['date', 'milk_time']
    search_fields = ['animal__tag_number', 'animal__name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Animal', {
            'fields': ('animal',)
        }),
        ('Production', {
            'fields': ('date', 'quantity_liters', 'milk_time', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== BREEDING RECORD ADMIN ====================
@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    list_display = ['animal', 'breeding_date', 'successful', 'expected_birth_date', 'offspring_count']
    list_filter = ['successful', 'breeding_date']
    search_fields = ['animal__tag_number', 'animal__name']
    date_hierarchy = 'breeding_date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Mother Animal', {
            'fields': ('animal',)
        }),
        ('Breeding Details', {
            'fields': ('breeding_date', 'successful', 'expected_birth_date', 'actual_birth_date')
        }),
        ('Offspring', {
            'fields': ('offspring_count', 'sire_animal', 'sire_name')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ==================== ANIMAL INCOME ADMIN ====================
@admin.register(AnimalIncome)
class AnimalIncomeAdmin(admin.ModelAdmin):
    list_display = ['animal', 'source', 'amount', 'date', 'description', 'buyer_name']
    list_filter = ['source', 'date']
    search_fields = ['description', 'animal__tag_number', 'animal__name', 'buyer_name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Animal', {
            'fields': ('animal',)
        }),
        ('Income Details', {
            'fields': ('source', 'amount', 'date', 'description')
        }),
        ('Buyer Information', {
            'fields': ('buyer_name', 'buyer_contact', 'notes'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal', 'user')


# ==================== ANIMAL EXPENSE ADMIN ====================
@admin.register(AnimalExpense)
class AnimalExpenseAdmin(admin.ModelAdmin):
    list_display = ['animal', 'category', 'amount', 'date', 'description', 'vendor_name']
    list_filter = ['category', 'date']
    search_fields = ['description', 'animal__tag_number', 'animal__name', 'vendor_name']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Animal', {
            'fields': ('animal',)
        }),
        ('Expense Details', {
            'fields': ('category', 'amount', 'date', 'description')
        }),
        ('Vendor Information', {
            'fields': ('vendor_name', 'vendor_contact', 'notes'),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal', 'user')