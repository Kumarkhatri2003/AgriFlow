from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# ==================== ANIMAL TYPE (Master Data) ====================
class AnimalType(models.Model):
    """Master list of animal types (Cow, Goat, Chicken, etc.)"""
    
    name = models.CharField(max_length=100)
    name_np = models.CharField(max_length=100, blank=True)
    
    avg_lifespan_years = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    gestation_days = models.IntegerField(null=True, blank=True)
    
    is_milk_animal = models.BooleanField(default=False)
    is_egg_animal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== ANIMAL (Main Model) ====================
class Animal(models.Model):
    """Individual animal owned by a farmer"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='animals')
    
    # Basic info
    animal_type = models.ForeignKey(AnimalType, on_delete=models.PROTECT, related_name='animals')
    name = models.CharField(max_length=100, blank=True)
    tag_number = models.CharField(max_length=50)
    
    # Birth/acquisition info
    birth_date = models.DateField(null=True, blank=True)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Gender
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('unknown', 'Unknown'),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unknown')
    
    # Current status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('dead', 'Dead'),
        ('butchered', 'Butchered'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Health and breeding
    is_pregnant = models.BooleanField(default=False)
    last_pregnancy_date = models.DateField(null=True, blank=True)
    expected_birth_date = models.DateField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['farmer', 'tag_number']
    
    def __str__(self):
        if self.name:
            return f"{self.animal_type} - {self.name} ({self.tag_number})"
        return f"{self.animal_type} - {self.tag_number}"
    
    # ============= FINANCIAL CALCULATIONS =====================
    @property
    def total_vaccination_cost(self):
        """Sum of all vaccination costs"""
        from django.db.models import Sum
        return self.vaccinations.aggregate(total=Sum('cost'))['total'] or 0
    
    @property
    def total_health_cost(self):
        """Sum of all health record costs"""
        from django.db.models import Sum
        return self.health_records.aggregate(total=Sum('cost'))['total'] or 0
    
    @property
    def total_medical_cost(self):
        """Total medical costs (vaccinations + health)"""
        return self.total_vaccination_cost + self.total_health_cost
    
    @property
    def total_other_expense(self):
        """Sum of all other expenses (feed, bedding, etc.)"""
        from django.db.models import Sum
        return self.expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def total_expense(self):
        """Total of ALL expenses (acquisition + medical + other)"""
        return (self.acquisition_cost + 
                self.total_vaccination_cost + 
                self.total_health_cost +
                self.total_other_expense)
    
    @property
    def total_income(self):
        """Sum of all income from this animal"""
        from django.db.models import Sum
        return self.incomes.aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def milk_income(self):
        """Income specifically from milk sales"""
        from django.db.models import Sum
        return self.incomes.filter(source='milk_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def egg_income(self):
        """Income specifically from egg sales"""
        from django.db.models import Sum
        return self.incomes.filter(source='egg_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def animal_sale_income(self):
        """Income from selling the animal itself"""
        from django.db.models import Sum
        return self.incomes.filter(source='animal_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def offspring_sale_income(self):
        """Income from selling offspring"""
        from django.db.models import Sum
        return self.incomes.filter(source='offspring_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def wool_income(self):
        """Income from wool sales"""
        from django.db.models import Sum
        return self.incomes.filter(source='wool_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def manure_income(self):
        """Income from manure sales"""
        from django.db.models import Sum
        return self.incomes.filter(source='manure_sale').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def subsidy_income(self):
        """Income from government subsidies"""
        from django.db.models import Sum
        return self.incomes.filter(source='subsidy').aggregate(total=Sum('amount'))['total'] or 0
    
    @property
    def net_profit(self):
        """Net profit (income - expenses)"""
        return self.total_income - self.total_expense
    
    @property
    def profit_margin(self):
        """Profit margin percentage"""
        if self.total_income > 0:
            return (self.net_profit / self.total_income) * 100
        return 0
    
    
    def __str__(self):
        if self.name:
            return f"{self.animal_type} - {self.name} ({self.tag_number})"
        return f"{self.animal_type} - {self.tag_number}"


# ==================== VACCINATION RECORDS ====================
class VaccinationRecord(models.Model):
    """Track vaccinations given to animals"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='vaccinations')
    
    vaccine_name = models.CharField(max_length=255)
    vaccine_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    
    administered_by = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-vaccine_date']
    
    def __str__(self):
        return f"{self.vaccine_name} - {self.animal} on {self.vaccine_date}"


# ==================== HEALTH RECORDS ====================
class HealthRecord(models.Model):
    """Track health issues, treatments, checkups"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    
    HEALTH_TYPES = [
        ('checkup', 'Regular Checkup'),
        ('sick', 'Sickness'),
        ('injury', 'Injury'),
        ('treatment', 'Treatment'),
        ('other', 'Other'),
    ]
    health_type = models.CharField(max_length=20, choices=HEALTH_TYPES, default='checkup')
    
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField(blank=True)
    treatment_date = models.DateField()
    follow_up_date = models.DateField(null=True, blank=True)
    
    vet_name = models.CharField(max_length=255, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-treatment_date']
    
    def __str__(self):
        return f"{self.get_health_type_display()} - {self.animal} on {self.treatment_date}"


# ==================== MILK RECORDS ====================
class MilkRecord(models.Model):
    """Track milk production for dairy animals"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='milk_records')
    
    date = models.DateField()
    quantity_liters = models.DecimalField(max_digits=8, decimal_places=2)
    
    MILK_TIMES = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('total', 'Total Day'),
    ]
    milk_time = models.CharField(max_length=20, choices=MILK_TIMES, default='total')
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['animal', 'date', 'milk_time']
    
    def __str__(self):
        return f"{self.animal} - {self.quantity_liters}L on {self.date}"


# ==================== BREEDING RECORDS ====================
class BreedingRecord(models.Model):
    """Track breeding and pregnancies"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='breeding_records')
    
    breeding_date = models.DateField()
    successful = models.BooleanField(default=False)
    
    # If successful
    expected_birth_date = models.DateField(null=True, blank=True)
    actual_birth_date = models.DateField(null=True, blank=True)
    offspring_count = models.IntegerField(default=0)
    
    # Sire (father) info
    sire_animal = models.ForeignKey(
        Animal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sired_offspring'
    )
    sire_name = models.CharField(max_length=255, blank=True)  # If sire not in system
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-breeding_date']
        unique_together = ['animal', 'breeding_date']
    
    def __str__(self):
        return f"{self.animal} bred on {self.breeding_date}"


# ==================== ANIMAL INCOME ====================
class AnimalIncome(models.Model):
    """Track income from animals (milk, egg, sale, etc.)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='animal_incomes')
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='incomes')
    
    INCOME_SOURCES = [
        ('milk_sale', 'Milk Sale'),
        ('egg_sale', 'Egg Sale'),
        ('animal_sale', 'Animal Sale'),
        ('offspring_sale', 'Offspring Sale'),
        ('wool_sale', 'Wool Sale'),
        ('manure_sale', 'Manure Sale'),
        ('subsidy', 'Government Subsidy'),
        ('other', 'Other Income'),
    ]
    
    source = models.CharField(max_length=50, choices=INCOME_SOURCES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    
    buyer_name = models.CharField(max_length=255, blank=True)
    buyer_contact = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_source_display()} - NPR {self.amount}"


# ==================== ANIMAL EXPENSES ====================
class AnimalExpense(models.Model):
    """Track other expenses for animals (feed, bedding, etc.)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='animal_expenses')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='expenses')
    
    EXPENSE_CATEGORIES = [
        ('feed', 'Feed'),
        ('bedding', 'Bedding'),
        ('equipment', 'Equipment'),
        ('breeding', 'Breeding Service'),
        ('transport', 'Transport'),
        ('other', 'Other'),
    ]
    
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    
    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_contact = models.CharField(max_length=100, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_category_display()} - NPR {self.amount}"