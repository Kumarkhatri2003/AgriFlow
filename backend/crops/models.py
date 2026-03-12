from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Crop(models.Model):
    """Main crop model"""
    
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

    # =============FINANCIAL CALCULATIONS=====================
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
    def total_other_expense(self):
        """Sum of all other expenses (labor, rent, seeds, etc.)"""
        from django.db.models import Sum
        return self.expenses.aggregate(total=Sum('amount'))['total'] or 0

    @property
    def total_expense(self):
        """Total of ALL expenses"""
        return self.total_fertilizer_cost + self.total_pesticide_cost + self.total_other_expense

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

    #Notice: fertilizer and pesticide are NOT in this list!
    EXPENSE_CATEGORIES = [
        ('seed', 'Seeds (बीउ)'),
        ('labor', 'Labor (ज्याला)'),
        ('land_rent', 'Land Rent (भाडा)'),
        ('irrigation', 'Irrigation (सिँचाइ)'),
        ('equipment', 'Equipment (उपकरण)'),
        ('transport', 'Transportation (ढुवानी)'),
        ('other', 'Other (अन्य)'),
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
        ('crop_sale', 'Crop Sale (बाली बिक्री)'),
        ('subsidy', 'Government Subsidy (अनुदान)'),
        ('insurance', 'Crop Insurance (बीमा)'),
        ('seed_sale', 'Seed Sale (बीउ बिक्री)'),
        ('other', 'Other Income (अन्य)'),
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