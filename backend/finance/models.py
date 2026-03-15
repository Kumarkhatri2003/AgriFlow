from django.db import models
from django.contrib.auth import get_user_model
from crops.models import Crop
from livestock.models import Animal

User = get_user_model()


class Transaction(models.Model):
    """Unified transaction model for all financial activities"""
    
    TRANSACTION_TYPES = [
        ('crop_income', 'Crop Income'),
        ('crop_expense', 'Crop Expense'),
        ('animal_income', 'Animal Income'),
        ('animal_expense', 'Animal Expense'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    
    # Basic info
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=100)  # Store category name
    
    # Optional links to specific entities
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    animal = models.ForeignKey(Animal, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For linking to original records
    source_id = models.CharField(max_length=100, blank=True)
    source_model = models.CharField(max_length=50, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.get_transaction_type_display()} - NPR {self.amount}"
    
    @property
    def is_income(self):
        return 'income' in self.transaction_type
    
    @property
    def formatted_amount(self):
        if self.is_income:
            return f"+ Rs. {self.amount:,.0f}"
        return f"- Rs. {self.amount:,.0f}"


class FinancialSummary(models.Model):
    """Store pre-calculated summaries for quick dashboard loading"""
    
    PERIOD_TYPES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_summaries')
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPES)
    
    # Period identification
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)
    day = models.IntegerField(null=True, blank=True)
    
    # Totals
    total_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_expense = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Breakdowns (stored as JSON for flexibility)
    income_by_category = models.JSONField(default=dict)
    expense_by_category = models.JSONField(default=dict)
    
    # Trend data (percentage change from previous period)
    income_trend = models.FloatField(default=0)
    expense_trend = models.FloatField(default=0)
    balance_trend = models.FloatField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'period_type', 'year', 'month', 'day']
        ordering = ['-year', '-month', '-day']
    
    def __str__(self):
        if self.period_type == 'daily':
            return f"{self.user.username} - {self.year}-{self.month:02d}-{self.day:02d}"
        elif self.period_type == 'monthly':
            return f"{self.user.username} - {self.year}-{self.month:02d}"
        return f"{self.user.username} - {self.year}"


class Category(models.Model):
    """Predefined categories for transactions (for dropdown)"""
    
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    name_np = models.CharField(max_length=100, blank=True)  # Nepali name
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    
    # For grouping
    group = models.CharField(max_length=50, blank=True)  # e.g., 'crop', 'animal'
    
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name', 'category_type']
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Budget(models.Model):
    """Monthly/Yearly budget planning"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    year = models.IntegerField()
    month = models.IntegerField(null=True, blank=True)  # null for yearly budget
    
    # Planned amounts
    planned_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    planned_expense = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Category-wise budgets (JSON)
    category_budgets = models.JSONField(default=dict)
    
    # Actual amounts (updated automatically)
    actual_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    actual_expense = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    
    # Alerts
    alert_threshold = models.IntegerField(default=80)  # Alert at 80% of budget
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'year', 'month']
    
    def __str__(self):
        if self.month:
            return f"{self.user.username} - {self.year}-{self.month:02d} Budget"
        return f"{self.user.username} - {self.year} Budget"
    
    @property
    def progress_income(self):
        if self.planned_income > 0:
            return (self.actual_income / self.planned_income) * 100
        return 0
    
    @property
    def progress_expense(self):
        if self.planned_expense > 0:
            return (self.actual_expense / self.planned_expense) * 100
        return 0
    
    @property
    def is_over_budget(self):
        return self.actual_expense > self.planned_expense