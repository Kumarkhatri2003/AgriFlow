from django.db import models
from django.contrib.auth import get_user_model
import uuid

from django.conf import settings
User = get_user_model()


class Crop(models.Model):
    """Main crop model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops')

    # Basic Information
    name = models.CharField(max_length=255)
    name_np = models.CharField(max_length=255, blank=True)
    variety = models.CharField(max_length=255, blank=True)

    # Field Information
    field_name = models.CharField(max_length=255)

    AREA_UNITS = [
        ('ropani', 'Ropani'),
        ('kattha', 'Kattha'),
        ('bigha', 'Bigha'),
        ('hectare', 'Hectare'),
    ]

    field_area = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit = models.CharField(max_length=50, choices=AREA_UNITS, default='ropani')

    # Dates
    planting_date = models.DateField()
    expected_harvest_date = models.DateField(null=True, blank=True)

    # Growth Information
    GROWTH_STAGES = [
        ('seeding', 'Seeding'),
        ('vegetative', 'Vegetative'),
        ('flowering', 'Flowering'),
        ('fruiting', 'Fruiting'),
        ('harvest', 'Harvest'),
    ]

    growth_stage = models.CharField(max_length=50, choices=GROWTH_STAGES, default='seeding')

    growth_stage_manual_override = models.BooleanField(
        default=False,
        help_text="If True, growth_stage was manually set by the user and will no longer be auto-calculated"
    )

    # Irrigation (simplified)
    is_irrigated = models.BooleanField(default=False, help_text="Is this crop irrigated?")

    soil_type = models.CharField(max_length=100, blank=True)

    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('harvested', 'Harvested'),
        ('done', 'Done'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ==================== FINANCIAL CALCULATIONS ====================

    @property
    def total_fertilizer_cost(self):
        """Sum of all fertilizer costs"""
        from django.db.models import Sum
        return self.fertilizers.aggregate(total=Sum('cost'))['total'] or 0

    @property
    def total_pesticide_cost(self):
        """Sum of all pesticide costs"""
        from django.db.models import Sum
        return self.pesticides.aggregate(total=Sum('cost'))['total'] or 0

    @property
    def total_labor_cost(self):
        """Sum of all labor costs"""
        from django.db.models import Sum
        return self.labour_records.aggregate(total=Sum('total_cost'))['total'] or 0

    @property
    def total_other_expense(self):
        """Sum of all other expenses (labor, rent, seeds, etc.)"""
        from django.db.models import Sum
        return self.expenses.aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_expense(self):
        """Total of ALL expenses"""
        return (
            self.total_fertilizer_cost
            + self.total_pesticide_cost
            + self.total_labor_cost
            + self.total_other_expense
        )

    @property
    def total_income(self):
        """Sum of all income"""
        from django.db.models import Sum
        return self.incomes.aggregate(total=Sum('amount'))['total'] or 0

    @property
    def net_profit(self):
        """Income minus total expenses"""
        return self.total_income - self.total_expense

    def __str__(self):
        return f"{self.name} - {self.field_name}"

    # ==================== GROWTH STAGE LOGIC ====================

    def calculate_growth_stage(self):
        """
        Auto-calculate the growth stage based on the planting date and
        crop configurations. Does NOT check the manual override flag —
        callers (update_growth_stage / save) are responsible for that.
        """
        if not self.planting_date:
            return 'seeding'

        from crops.services.config_matcher import CropConfigMatcher
        from datetime import date, datetime

        planting_date = self.planting_date
        if isinstance(planting_date, str):
            try:
                planting_date = datetime.strptime(planting_date, '%Y-%m-%d').date()
            except ValueError:
                return 'seeding'

        # Get farmer's region
        farmer_region = getattr(self.farmer, 'geographical_region', None)

        # Find matching config - wrap in try-except to handle any errors
        try:
            config, match_strategy = CropConfigMatcher.find_best_match(
                crop_name=self.name,
                variety=self.variety if self.variety else None,
                region=farmer_region,
                planting_date=planting_date
            )
        except Exception:
            # If any error occurs (like MultipleObjectsReturned), just return current stage
            return self.growth_stage

        if not config:
            # No config found - this is a custom crop (user selected "Other")
            return self.growth_stage if self.growth_stage else 'seeding'

        days_since = (date.today() - planting_date).days
        if days_since < 0:
            days_since = 0

        stage_name = config.get_stage_name(days_since)

        # Map CropTypeConfig stage name to Crop growth stage choice
        mapping = {
            'germination': 'seeding',
            'seeding': 'seeding',
            'vegetative': 'vegetative',
            'flowering': 'flowering',
            'maturation': 'fruiting',
            'fruiting': 'fruiting',
            'harvest': 'harvest',
            'completed': 'harvest',
        }

        return mapping.get(stage_name, 'seeding')

    def update_growth_stage(self, save=True):
        """
        Calculate and update the growth stage of the crop.
        No-op if the user has manually overridden the stage — once
        growth_stage_manual_override is True this never runs again.
        """
        if self.growth_stage_manual_override:
            return self.growth_stage

        try:
            new_stage = self.calculate_growth_stage()
        except Exception:
            # If any error occurs, don't break the caller
            return self.growth_stage

        if self.growth_stage != new_stage:
            self.growth_stage = new_stage
            if save:
                self.save(update_fields=['growth_stage'])

        return self.growth_stage

    def set_manual_growth_stage(self, stage, save=True):
        """
        Explicitly called when the user manually sets the growth stage
        (e.g. from the serializer). Locks out auto-calculation permanently
        for this crop.
        """
        self.growth_stage = stage
        self.growth_stage_manual_override = True
        if save:
            self.save(update_fields=['growth_stage', 'growth_stage_manual_override'])
        return self.growth_stage

    def reset_growth_stage_to_auto(self, save=True):
        """
        Optional escape hatch: turns auto-calculation back on and
        immediately recalculates. Not called anywhere by default.
        """
        self.growth_stage_manual_override = False
        if save:
            self.save(update_fields=['growth_stage_manual_override'])
        return self.update_growth_stage(save=save)

    def save(self, *args, **kwargs):
        from datetime import date, timedelta
        
        # 1. Detect if planting date has changed
        planting_date_changed = False
        if self.pk:
            try:
                original = Crop.objects.get(pk=self.pk)
                if original.planting_date != self.planting_date:
                    planting_date_changed = True
                    self.growth_stage_manual_override = False
            except Crop.DoesNotExist:
                pass

        # 2. Determine expected harvest date for auto-harvest logic
        expected_harvest = self.expected_harvest_date
        if not expected_harvest and self.planting_date:
            from crops.services.config_matcher import CropConfigMatcher
            farmer_region = getattr(self.farmer, 'geographical_region', None)
            try:
                config, _ = CropConfigMatcher.find_best_match(
                    crop_name=self.name,
                    variety=self.variety if self.variety else None,
                    region=farmer_region,
                    planting_date=self.planting_date
                )
                if config:
                    expected_harvest = self.planting_date + timedelta(days=config.total_growing_days)
            except Exception:
                pass

        # 3. Calculate status and growth stage
        modified_fields = set()
        
        # Check if the system date has passed the expected harvest date
        if expected_harvest and date.today() > expected_harvest:
            if self.status != 'harvested':
                self.status = 'harvested'
                modified_fields.add('status')
            if self.growth_stage != 'harvest':
                self.growth_stage = 'harvest'
                modified_fields.add('growth_stage')
        else:
            # Standard auto-calculate growth stage if not manually overridden
            if not self.growth_stage_manual_override:
                try:
                    new_stage = self.calculate_growth_stage()
                    if self.growth_stage != new_stage:
                        self.growth_stage = new_stage
                        modified_fields.add('growth_stage')
                except Exception:
                    pass

        if planting_date_changed:
            modified_fields.add('growth_stage_manual_override')

        # 4. Handle update_fields if passed
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            update_fields = set(update_fields)
            # If we changed any fields, ensure they are written to the database
            for field in modified_fields:
                update_fields.add(field)
            kwargs['update_fields'] = list(update_fields)

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
   
    


# ==================== FERTILIZER RECORDS ====================
class FertilizerRecord(models.Model):
    """Track fertilizers Records"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fertilizer_records')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='fertilizers')

    FERTILIZER_TYPES = [
        ('chemical', 'Chemical'),
        ('organic', 'Organic'),
        ('bio', 'Bio-fertilizer'),
    ]
    fertilizer_type = models.CharField(max_length=50, choices=FERTILIZER_TYPES, default='chemical')
    name = models.CharField(max_length=255)

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    
    # COST 
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    application_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.quantity}{self.unit} (NPR {self.cost})"

    class Meta:
        ordering = ['-application_date']


# ==================== PESTICIDE RECORDS ====================
class PesticideRecord(models.Model):
    """Track pesticides Records"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pesticide_records')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='pesticides')

    name = models.CharField(max_length=255)
    target_pest = models.CharField(max_length=255, blank=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    UNIT_CHOICES = [
        ('ml', 'Milliliters'),
        ('l', 'Liters'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='ml')
    
    #COST
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    application_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.target_pest:
            return f"{self.name} (for {self.target_pest}) - NPR {self.cost}"
        return f"{self.name} - NPR {self.cost}"

    class Meta:
        ordering = ['-application_date']


# ==================== CROP EXPENSES (OTHER) ====================
class CropExpense(models.Model):
    """Track OTHER expenses - seeds, labor, rent, etc. 
    NOT for fertilizers/pesticides - those go in their own models"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_expenses')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='expenses')

   
    EXPENSE_CATEGORIES = [
        ('seed', 'Seeds'),
        ('labor', 'Labor '),
        ('land_rent', 'Land Rent'),
        ('irrigation', 'Irrigation'),
        ('equipment', 'Equipment'),
        ('transport', 'Transportation'),
        ('other', 'Other'),
    ]

    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    # Vendor information
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_contact = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_category_display()} - NPR {self.amount} on {self.date}"


# ==================== CROP INCOME ====================
class CropIncome(models.Model):
    """Track income from crops"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_incomes')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='incomes')

    INCOME_SOURCES = [
        ('crop_sale', 'Crop Sale'),
        ('subsidy', 'Government Subsidy'),
        ('insurance', 'Crop Insurance'),
        ('seed_sale', 'Seed Sale'),
        ('other', 'Other Income'),
    ]

    source = models.CharField(max_length=50, choices=INCOME_SOURCES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    # Buyer information
    buyer_name = models.CharField(max_length=255, blank=True)
    buyer_contact = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_source_display()} - NPR {self.amount} on {self.date}"


# ==================== HARVEST RECORDS ====================
class HarvestRecord(models.Model):
    """Track harvest details and yield"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='harvest_records')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='harvests')

    harvest_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('quintal', 'Quintal'),
        ('ton', 'Ton'),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')

    # Quality grade
    QUALITY_CHOICES = [
        ('premium', 'Premium'),
        ('standard', 'Standard'),
        ('low', 'Low Grade'),
    ]
    quality = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='standard')

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-harvest_date']

    def __str__(self):
        return f"{self.crop.name} - {self.quantity}{self.unit} on {self.harvest_date}"


class Labour(models.Model):
    """Track labor details for crop activities"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labour_records')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='labour_records')
    
    name = models.CharField(max_length=255)
    workers_count = models.PositiveIntegerField(default=1)
    days = models.PositiveIntegerField(default=1)
    rate_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate total cost
        self.total_cost = self.workers_count * self.days * self.rate_per_day
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.workers_count} workers × {self.days} days"

    class Meta:
        ordering = ['-date']
        
        

class CropKnowledgeBase(models.Model):
    # Basic info
    name_en = models.CharField(max_length=100, unique=True)
    name_np = models.CharField(max_length=100, blank=True)
    
    CATEGORY_CHOICES = [
        ('cereal', 'Cereal'),
        ('pulse', 'Pulse'),
        ('cash_crop', 'Cash Crop'),
        ('vegetable', 'Vegetable'),
        ('tuber', 'Tuber'),
        ('oilseed', 'Oilseed')
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    # Season
    SEASON_CHOICES = [
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('monsoon', 'Monsoon'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ]
    best_season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    other_seasons = models.CharField(max_length=200, blank=True, help_text="Comma separated: spring,autumn")
    
    # Temperature
    temp_min = models.FloatField(help_text="Minimum temperature (°C)")
    temp_max = models.FloatField(help_text="Maximum temperature (°C)")
    temp_ideal = models.FloatField(help_text="Ideal temperature (°C)")
    
    # Soil
    soil_ideal = models.CharField(max_length=50)
    soil_other = models.CharField(max_length=200, blank=True, help_text="Comma separated: clay,silty")
    
    # pH
    ph_min = models.FloatField()
    ph_max = models.FloatField()
    ph_ideal = models.FloatField()
    
     # Tolerances
    DROUGHT_CHOICES = [
        ('low', 'Low'), 
        ('medium', 'Medium'), 
        ('high', 'High')
        ]
    drought_tolerance = models.CharField(max_length=10, choices=DROUGHT_CHOICES)
    
    FROST_CHOICES = [
    ('yes', 'Yes (Frost kills it)'),
    ('no', 'No (Tolerant)'),
    ('tolerant', 'Tolerant (May survive light frost)'),
    ]
    
    frost_sensitive = models.CharField(max_length=10, choices=FROST_CHOICES, default='no')
    # Water & Region
    WATER_CHOICES = [
        ('low', 'Low'), 
        ('medium', 'Medium'), 
        ('high', 'High')
        ]
    water_req = models.CharField(max_length=10, choices=WATER_CHOICES)
    
    water_logging_tolerance = models.CharField(max_length=10, choices=DROUGHT_CHOICES, default='medium')

    region_suitable = models.CharField(max_length=200, help_text="Comma separated: terai,mid-hill,hill,mountain")
    
    
   
   
    day_length_sensitive = models.BooleanField(default=False)
    day_length_type = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('short-day', 'Short Day'),
        ('long-day', 'Long Day'),
        ('day-neutral', 'Day Neutral'),
    ])
    
    # Growth
    growing_days = models.IntegerField(default=100)
    altitude_min = models.IntegerField(default=0)
    altitude_max = models.IntegerField(default=3000)
    # Labor & Storage
    LABOR_CHOICES = [
        ('low', 'Low'), 
        ('medium', 'Medium'), 
        ('high', 'High')
        ]
    labor_req = models.CharField(max_length=10, choices=LABOR_CHOICES)
    
    STORAGE_CHOICES = [
        ('very_short', 'Very Short (<1 week)'),
        ('short', 'Short (1-4 weeks)'),
        ('medium', 'Medium (1-3 months)'),
        ('long', 'Long (>3 months)'),
    ]
    storage_life = models.CharField(max_length=20, choices=STORAGE_CHOICES)
    
    # NPK needs
    n_need = models.FloatField(default=60, help_text="Nitrogen requirement (kg/hectare) - Low:20-40, Medium:40-80, High:80-120")
    p_need = models.FloatField(default=40, help_text="Phosphorus requirement (kg/hectare) - Low:10-30, Medium:30-60, High:60-90")
    k_need = models.FloatField(default=40, help_text="Potassium requirement (kg/hectare) - Low:10-30, Medium:30-60, High:60-90")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name_en']
    
    def __str__(self):
        return self.name_en
    
class CropRecommendationHistory(models.Model):
    """
    Stores farmer inputs exactly as expert system expects
    """
    
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Required fields
    region = models.CharField(max_length=50, choices=[
        ('terai', 'Terai'),
        ('mid-hill', 'Mid-Hill'),
        ('hill', 'Hill'),
        ('mountain', 'Mountain'),
    ])
    
    season = models.CharField(max_length=20, choices=[
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('monsoon', 'Monsoon'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    ])
    
    water_source = models.CharField(max_length=50, choices=[
        ('rainfed_only', 'Rainfed Only'),
        ('canal', 'Canal'),
        ('well', 'Well'),
        ('river', 'River'),
        ('drip_irrigation', 'Drip Irrigation'),
    ], default='rainfed_only')
    
    soil_type = models.CharField(max_length=50, choices=[
        ('clay', 'Clay'),
        ('loamy', 'Loamy'),
        ('sandy', 'Sandy'),
        ('silty', 'Silty'),
        ('clay_loam', 'Clay Loam'),
    ])
    
    labor_availability = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='medium')
    
    market_distance = models.CharField(max_length=20, choices=[
        ('near', 'Near'),
        ('medium', 'Medium'),
        ('far', 'Far'),
    ], default='near')
    
    farming_goal = models.CharField(max_length=20, choices=[
        ('profit', 'Profit'),
        ('food_security', 'Food Security'),
        ('mixed', 'Mixed'),
        ('subsistence', 'Subsistence'),
    ], default='mixed')
    
    # ========== ADD THESE MISSING FIELDS ==========
    DROUGHT_RISK_CHOICES = [
        ('high', 'High Risk'),
        ('medium', 'Medium Risk'),
        ('low', 'Low Risk'),
    ]
    drought_risk = models.CharField(
        max_length=10,
        choices=DROUGHT_RISK_CHOICES,
        default='medium',
        help_text="Drought risk level at farm location"
    )
    
    temperature = models.FloatField(
        null=True,
        blank=True,
        help_text="Temperature in °C"
    )
    
    frost_risk = models.BooleanField(
        default=False,
        help_text="Does your area experience frost?"
    )
    # =============================================
    
    # Optional soil test fields
    ph = models.FloatField(null=True, blank=True)
    n = models.FloatField(null=True, blank=True, help_text="Nitrogen kg/ha")
    p = models.FloatField(null=True, blank=True, help_text="Phosphorus kg/ha")
    k = models.FloatField(null=True, blank=True, help_text="Potassium kg/ha")
    
    # Results
    recommendations = models.JSONField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.farmer.username} - {self.created_at.date()}"
    
    
   
    
class CropTypeConfig(models.Model):

    REGION_CHOICES = [
        ('terai', 'Terai'),
        ('hilly', 'Hilly'),
        ('himalayan', 'Himalayan'),
    ]
    
    SEASON_CHOICES = [
        ('spring', 'Spring (Feb-Apr)'),
        ('summer', 'Summer (May-Jul)'),
        ('monsoon', 'Monsoon (Jun-Sep)'),
        ('autumn', 'Autumn (Sep-Nov)'),
        ('winter', 'Winter (Dec-Feb)'),
    ]

    # Identification fields
    crop_name = models.CharField(max_length=100)
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    variety = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional variety name"
    )
    
    season = models.CharField(
        max_length=20, 
        choices=SEASON_CHOICES, 
        blank=True, null=True, 
        help_text="Growing season"
        )


    # Stage 1: Germination
    germination_start_day = models.IntegerField(default=0)
    germination_end_day = models.IntegerField(default=10)

    # Stage 2: Vegetative
    vegetative_start_day = models.IntegerField(default=11)
    vegetative_end_day = models.IntegerField(default=40)

    # Stage 3: Flowering/Reproductive
    flowering_start_day = models.IntegerField(default=41)
    flowering_end_day = models.IntegerField(default=60)

    # Stage 4: Maturation/Fruiting
    maturation_start_day = models.IntegerField(default=61)
    maturation_end_day = models.IntegerField(default=85)

    # Stage 5: Harvest
    harvest_start_day = models.IntegerField(default=86)
    harvest_end_day = models.IntegerField(default=120)

    total_growing_days = models.IntegerField(default=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ['crop_name', 'region', 'variety', 'season']
        indexes = [
            models.Index(fields=['crop_name', 'region', 'variety', 'season']),
            models.Index(fields=['crop_name', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['crop_name', 'variety', 'region', 'season'],
                name='unique_crop_config'
            )
        ]
       

    def __str__(self):
       return self.get_display_name()
   
    def get_display_name(self):
        """Generate human-readable display name"""
        
        parts = [self.crop_name]
        if self.variety:
            parts.append(f"({self.variety})")
        
        if self.region:
            parts.append(f"- {self.get_region_display()}") 
        
        if self.season:
            parts.append(f"[{self.get_season_display()}]") 
            
        return " ".join(parts)    
    
    def get_region_display(self):
        region_names = {
            'terai': 'Terai',
            'hilly': 'Hilly',
            'himalayan': 'Himalayan',
        }
        return region_names.get(self.region, self.region or 'Any')
    
    def get_season_display(self):
        season_names = {
            'spring': 'Spring',
            'summer': 'Summer',
            'monsoon': 'Monsoon',
            'autumn': 'Autumn',
            'winter': 'Winter',
        }
        return season_names.get(self.season, self.season or 'Any')

    def get_stage_name(self, days_after_planting):
        if days_after_planting <= self.germination_end_day:
            return 'germination'
        elif days_after_planting <= self.vegetative_end_day:
            return 'vegetative'
        elif days_after_planting <= self.flowering_end_day:
            return 'flowering'
        elif days_after_planting <= self.maturation_end_day:
            return 'maturation'
        elif days_after_planting <= self.harvest_end_day:
            return 'harvest'
        return 'completed'

    def get_stage_display_name(self, days_after_planting):
        stage = self.get_stage_name(days_after_planting)
        return {
            'germination': 'Germination',
            'vegetative': 'Vegetative',
            'flowering': 'Flowering',
            'maturation': 'Maturation',
            'harvest': 'Harvest',
            'completed': 'Completed'
        }.get(stage, 'Unknown')
        
    def get_stage_start_day(self, stage_name):
        """Get start day for a given stage"""
        stage_starts = {
            'germination': self.germination_start_day,
            'vegetative': self.vegetative_start_day,
            'flowering': self.flowering_start_day,
            'maturation': self.maturation_start_day,
            'harvest': self.harvest_start_day,
        }
        return stage_starts.get(stage_name, 0)
        
        
class CropActivityRule(models.Model):
    STAGE_CHOICE = [
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative'),
        ('flowering', 'Flowering'),
        ('maturation', 'Maturation'),
        ('harvest', 'Harvest'),
    ]  
    
    crop_config = models.ForeignKey(
        CropTypeConfig,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    
    growth_stage = models.CharField(max_length=20, choices=STAGE_CHOICE)
    
    title = models.CharField(max_length=200)
    title_np = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    description_np = models.TextField(blank=True)
    
    
    # Optional details
    measurements = models.TextField(blank=True, help_text="e.g., Urea: 4.8 Kg/Ropani")
    target_pest = models.TextField(blank=True, help_text="e.g., Blast, Bacterial leaf blight")
    recommendations = models.TextField(blank=True, help_text="Additional tips for farmers")
    
    # Timing: 0 = any day in stage, or specific day like 10
    day_offset = models.IntegerField(
        default=0,
        help_text="0 = any day in this stage, or specific day number (e.g., 10 = exactly on day 10 of the stage)"
    )
    
    order = models.IntegerField(default=0, help_text = "Lower number = shown first")
    
    #status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ['crop_config', 'growth_stage', 'order', 'day_offset']
        indexes = [
            models.Index(fields=['crop_config', 'growth_stage', 'is_active']),
            models.Index(fields=['growth_stage', 'is_active']),
        ]
        unique_together = ['crop_config', 'growth_stage', 'title']
        
    def __str__(self):
        return f"{self.crop_config.crop_name} - {self.get_growth_stage_display()}: {self.title}" 
    
    def get_growth_stage_display(self):
        stage_icons = {
            'germination': '🌱',
            'vegetative': '🌿',
            'flowering': '🌸',
            'maturation': '🍎',
            'harvest': '✂️',
        }
        icon = stage_icons.get(self.growth_stage, '📋')
        name = self.growth_stage.capitalize()
        return f"{icon} {name}"     
    