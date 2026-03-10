from django.contrib import admin
from .models import AnimalType, Animal, VaccinationRecord, HealthRecord, MilkRecord, BreedingRecord

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
    fk_name = 'animal'  # 👈 ADD THIS - tells admin to use 'animal' field, not 'sire_animal'
    extra = 0
    fields = ['breeding_date', 'successful', 'expected_birth_date', 'offspring_count']
    readonly_fields = ['created_at']


# ==================== ANIMAL ADMIN ====================
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ['tag_number', 'name', 'animal_type', 'farmer', 'gender', 'status', 'is_pregnant']
    list_filter = ['animal_type', 'gender', 'status', 'is_pregnant']
    search_fields = ['tag_number', 'name', 'farmer__email', 'farmer__username']
    readonly_fields = ['created_at', 'updated_at']
    
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
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [VaccinationInline, HealthInline, MilkInline, BreedingInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('animal_type', 'farmer')


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