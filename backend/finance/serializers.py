from rest_framework import serializers
from .models import Transaction, FinancialSummary, Category, Budget


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    is_income = serializers.BooleanField(read_only=True)
    formatted_amount = serializers.CharField(read_only=True)
    
    crop_name = serializers.CharField(source='crop.name', read_only=True, default=None)
    crop_field_name = serializers.CharField(source='crop.field_name', read_only=True, default=None)
        
        
    animal_name = serializers.CharField(source='animal.name', read_only=True, default=None)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True, default=None)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'transaction_type_display',
            'date', 'amount', 'formatted_amount', 'description', 'category',
            'is_income', 'crop', 'crop_name','crop_field_name', 'animal', 'animal_name', 'animal_tag',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating manual transactions"""
    
    class Meta:
        model = Transaction
        fields = [
            'id','transaction_type', 'date', 'amount', 'description', 
            'category', 'crop', 'animal', 'notes'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_date(self, value):
        from datetime import date
        if value > date.today():
            raise serializers.ValidationError("Date cannot be in the future")
        return value


class FinancialSummarySerializer(serializers.ModelSerializer):
    """Serializer for financial summaries"""
    
    class Meta:
        model = FinancialSummary
        fields = [
            'period_type', 'year', 'month', 'day',
            'total_income', 'total_expense', 'net_balance',
            'income_by_category', 'expense_by_category',
            'income_trend', 'expense_trend', 'balance_trend'
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_np', 'category_type', 'category_type_display',
            'group', 'is_default', 'is_active'
        ]


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for budgets"""
    
    progress_income = serializers.FloatField(read_only=True)
    progress_expense = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'year', 'month',
            'planned_income', 'planned_expense',
            'actual_income', 'actual_expense',
            'category_budgets',
            'progress_income', 'progress_expense',
            'is_over_budget', 'alert_threshold',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'actual_income', 'actual_expense', 'created_at', 'updated_at']


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data"""
    
    total_income = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=14, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=14, decimal_places=2)
    
    income_trend = serializers.FloatField()
    expense_trend = serializers.FloatField()
    balance_trend = serializers.FloatField()
    
    recent_transactions = TransactionSerializer(many=True)
    expense_breakdown = serializers.ListField()
    monthly_trend = serializers.ListField()