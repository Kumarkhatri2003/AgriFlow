from rest_framework import serializers
from .models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord
)

# ==================== FERTILIZER SERIALIZER ====================
class FertilizerRecordSerializer(serializers.ModelSerializer):
    """Serializer for fertilizer records"""
    
    fertilizer_type_display = serializers.CharField(source='get_fertilizer_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FertilizerRecord
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'fertilizer_type', 'fertilizer_type_display', 'name',
            'quantity', 'unit', 'unit_display', 'cost',
            'application_date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


# ==================== PESTICIDE SERIALIZER ====================
class PesticideRecordSerializer(serializers.ModelSerializer):
    """Serializer for pesticide records"""
    
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PesticideRecord
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'name', 'target_pest',
            'quantity', 'unit', 'unit_display', 'cost',
            'application_date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


# ==================== CROP EXPENSE SERIALIZER ====================
class CropExpenseSerializer(serializers.ModelSerializer):
    """Serializer for crop expenses (other than fertilizer/pesticide)"""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CropExpense
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'category', 'category_display', 'amount', 'date',
            'description', 'vendor_name', 'vendor_contact',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


# ==================== CROP INCOME SERIALIZER ====================
class CropIncomeSerializer(serializers.ModelSerializer):
    """Serializer for crop income"""
    
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CropIncome
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'source', 'source_display', 'amount', 'date',
            'description', 'buyer_name', 'buyer_contact',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


# ==================== HARVEST RECORD SERIALIZER ====================
class HarvestRecordSerializer(serializers.ModelSerializer):
    """Serializer for harvest records"""
    
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)
    quality_display = serializers.CharField(source='get_quality_display', read_only=True)
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = HarvestRecord
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'harvest_date', 'quantity', 'unit', 'unit_display',
            'quality', 'quality_display', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


# ==================== MAIN CROP SERIALIZER ====================
class CropSerializer(serializers.ModelSerializer):
    """Complete Crop serializer with all related data"""
    
    # Display fields
    area_unit_display = serializers.CharField(source='get_area_unit_display', read_only=True)
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # User info
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    # Related records
    fertilizers = FertilizerRecordSerializer(many=True, read_only=True)
    pesticides = PesticideRecordSerializer(many=True, read_only=True)
    expenses = CropExpenseSerializer(many=True, read_only=True)
    incomes = CropIncomeSerializer(many=True, read_only=True)
    harvests = HarvestRecordSerializer(many=True, read_only=True)
    
    # Financial calculations (properties from model)
    total_fertilizer_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pesticide_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_other_expense = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Crop
        fields = [
            # Basic info
            'id', 'farmer', 'farmer_username',
            'name', 'name_np', 'variety',
            'field_name', 'field_area', 'area_unit', 'area_unit_display',
            'planting_date', 'expected_harvest_date',
            'growth_stage', 'growth_stage_display',
            'is_irrigated', 'soil_type',
            'status', 'status_display',
            'notes', 'created_at', 'updated_at',
            
            # Related records
            'fertilizers', 'pesticides', 'expenses', 'incomes', 'harvests',
            
            # Financial calculations
            'total_fertilizer_cost', 'total_pesticide_cost', 'total_other_expense',
            'total_expense', 'total_income', 'net_profit'
        ]
        read_only_fields = ['id', 'farmer', 'created_at', 'updated_at']


# ==================== CREATE/UPDATE SERIALIZERS ====================

class FertilizerRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating fertilizer records"""
    
    class Meta:
        model = FertilizerRecord
        fields = ['fertilizer_type', 'name', 'quantity', 'unit', 'cost', 'application_date', 'notes']
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value


class PesticideRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating pesticide records"""
    
    class Meta:
        model = PesticideRecord
        fields = ['name', 'target_pest', 'quantity', 'unit', 'cost', 'application_date', 'notes']
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value


class CropExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating crop expenses"""
    
    class Meta:
        model = CropExpense
        fields = ['category', 'amount', 'date', 'description', 'vendor_name', 'vendor_contact', 'notes']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class CropIncomeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating crop income"""
    
    class Meta:
        model = CropIncome
        fields = ['source', 'amount', 'date', 'description', 'buyer_name', 'buyer_contact', 'notes']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value


class HarvestRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating harvest records"""
    
    class Meta:
        model = HarvestRecord
        fields = ['harvest_date', 'quantity', 'unit', 'quality', 'notes']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value