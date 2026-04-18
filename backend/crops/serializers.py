from rest_framework import serializers
from .models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord,Labour,CropKnowledgeBase,CropRecommendationHistory
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
    
class LaborSerializer(serializers.ModelSerializer):
    """Serializer for labor records"""
    
    crop_name = serializers.CharField(source='crop.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Labour
        fields = [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'name', 'workers_count', 'days', 'rate_per_day', 'total_cost',
            'date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'total_cost']


class LaborCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating labor records"""
    
    class Meta:
        model = Labour
        fields = ['name', 'workers_count', 'days', 'rate_per_day', 'date', 'notes']
    
    def validate_workers_count(self, value):
        if value <= 0:
            raise serializers.ValidationError("Workers count must be greater than 0")
        return value
    
    def validate_days(self, value):
        if value <= 0:
            raise serializers.ValidationError("Days must be greater than 0")
        return value
    
    def validate_rate_per_day(self, value):
        if value <= 0:
            raise serializers.ValidationError("Rate per day must be greater than 0")
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
    labour_records = LaborSerializer(many=True, read_only=True)
    
    # Financial calculations (properties from model)
    total_fertilizer_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pesticide_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_other_expense = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_labor_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
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
            'fertilizers', 'pesticides', 'expenses', 'incomes', 'harvests','labour_records',
            
            # Financial calculations
            'total_fertilizer_cost', 'total_pesticide_cost', 'total_other_expense',
            'total_expense', 'total_income', 'net_profit', 'total_labor_cost'
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
    
    
        
from rest_framework import serializers
from .models import CropKnowledgeBase, CropRecommendationHistory
import re


class CropKnowledgeBaseSerializer(serializers.ModelSerializer):
    """Serializer for the crop knowledge base – matches final engine fields"""
    
    # Display choices
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    best_season_display = serializers.CharField(source='get_best_season_display', read_only=True)
    water_req_display = serializers.CharField(source='get_water_req_display', read_only=True)
    drought_tolerance_display = serializers.CharField(source='get_drought_tolerance_display', read_only=True)
    labor_req_display = serializers.CharField(source='get_labor_req_display', read_only=True)
    storage_life_display = serializers.CharField(source='get_storage_life_display', read_only=True)
    
    # Helper lists (properties on model)
    all_seasons = serializers.ListField(read_only=True)
    regions_suitable = serializers.ListField(read_only=True)
    acceptable_soils = serializers.ListField(read_only=True)
    
    # NPK level fields
    n_need_level = serializers.SerializerMethodField()
    p_need_level = serializers.SerializerMethodField()
    k_need_level = serializers.SerializerMethodField()

    class Meta:
        model = CropKnowledgeBase
        fields = [
            'id', 'name_en', 'name_np', 'category', 'category_display',
            'best_season', 'best_season_display', 'other_seasons', 'all_seasons',
            'temp_min', 'temp_max', 'temp_ideal',
            'soil_ideal', 'soil_other', 'acceptable_soils',
            'ph_min', 'ph_max', 'ph_ideal',
            'water_req', 'water_req_display',
            'region_suitable', 'regions_suitable',
            'drought_tolerance', 'drought_tolerance_display',
            'frost_sensitive',
            'labor_req', 'labor_req_display',
            'storage_life', 'storage_life_display',
            'n_need', 'p_need', 'k_need',
            'n_need_level', 'p_need_level', 'k_need_level',
        ]
        read_only_fields = ['id']
    
    def get_n_need_level(self, obj):
        if obj.n_need <= 40:
            return 'low'
        elif obj.n_need <= 80:
            return 'medium'
        else:
            return 'high'
    
    def get_p_need_level(self, obj):
        if obj.p_need <= 30:
            return 'low'
        elif obj.p_need <= 60:
            return 'medium'
        else:
            return 'high'
    
    def get_k_need_level(self, obj):
        if obj.k_need <= 30:
            return 'low'
        elif obj.k_need <= 60:
            return 'medium'
        else:
            return 'high'
    
    def validate_name_en(self, value):
        """Validate English name"""
        if not value or not value.strip():
            raise serializers.ValidationError("English name is required")
        if len(value) > 100:
            raise serializers.ValidationError("English name cannot exceed 100 characters")
        return value.strip()
    
    def validate_temp_min(self, value):
        """Validate minimum temperature"""
        if value is None:
            raise serializers.ValidationError("Minimum temperature is required")
        if value < -20 or value > 50:
            raise serializers.ValidationError("Temperature must be between -20°C and 50°C")
        return value
    
    def validate_temp_max(self, value):
        """Validate maximum temperature"""
        if value is None:
            raise serializers.ValidationError("Maximum temperature is required")
        if value < -20 or value > 50:
            raise serializers.ValidationError("Temperature must be between -20°C and 50°C")
        return value
    
    def validate(self, data):
        """Cross-field validations"""
        # Check temp_min <= temp_max
        if 'temp_min' in data and 'temp_max' in data:
            if data['temp_min'] > data['temp_max']:
                raise serializers.ValidationError({
                    'temp_min': "Minimum temperature cannot be greater than maximum temperature"
                })
        
        # Check ph_min <= ph_max
        if 'ph_min' in data and 'ph_max' in data:
            if data['ph_min'] > data['ph_max']:
                raise serializers.ValidationError({
                    'ph_min': "Minimum pH cannot be greater than maximum pH"
                })
        
        # Check ph_ideal is within range
        if 'ph_ideal' in data and 'ph_min' in data and 'ph_max' in data:
            if not (data['ph_min'] <= data['ph_ideal'] <= data['ph_max']):
                raise serializers.ValidationError({
                    'ph_ideal': f"Ideal pH must be between {data['ph_min']} and {data['ph_max']}"
                })
        
        return data


class CropRecommendationRequestSerializer(serializers.Serializer):
    """Serializer for crop recommendation requests with full validation"""
    
    # Basic fields
    region = serializers.ChoiceField(
        choices=['terai', 'mid-hill', 'hill', 'mountain'],
        default='terai',
        error_messages={
            'invalid_choice': 'Invalid region. Choose from: terai, mid-hill, hill, mountain'
        }
    )
    
    season = serializers.ChoiceField(
        choices=['spring', 'monsoon', 'autumn', 'winter'],
        required=False,
        allow_null=True,
        help_text="Leave empty to auto-detect current season",
        error_messages={
            'invalid_choice': 'Invalid season. Choose from: spring, monsoon, autumn, winter'
        }
    )
    
    water_source = serializers.ChoiceField(
        choices=['rainfed_only', 'seasonal_canal', 'well_borewell', 'drip_irrigation'],
        default='rainfed_only',
        error_messages={
            'invalid_choice': 'Invalid water source. Choose from: rainfed_only, seasonal_canal, well_borewell, drip_irrigation'
        }
    )
    
    soil_type = serializers.CharField(
        max_length=50,
        default='loamy',
        error_messages={
            'max_length': 'Soil type cannot exceed 50 characters'
        }
    )
    
    labor_availability = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        default='medium',
        error_messages={
            'invalid_choice': 'Invalid labor availability. Choose from: low, medium, high'
        }
    )
    
    market_distance = serializers.ChoiceField(
        choices=['near', 'far'],
        default='near',
        error_messages={
            'invalid_choice': 'Invalid market distance. Choose from: near, far'
        }
    )
    
    farming_goal = serializers.ChoiceField(
        choices=['food_security', 'profit', 'mixed'],
        default='mixed',
        error_messages={
            'invalid_choice': 'Invalid farming goal. Choose from: food_security, profit, mixed'
        }
    )
    
    temperature_override = serializers.FloatField(
        required=False,
        allow_null=True,
        help_text="Optional: override automatic temperature based on region/season"
    )
    
    elevation_risk = serializers.BooleanField(
        required=False,
        default=None,
        allow_null=True,
        help_text="If not provided, auto-derived from region+season"
    )
    
    # NPK Fields
    ph = serializers.FloatField(
        min_value=0,
        max_value=14,
        required=False,
        allow_null=True,
        error_messages={
            'min_value': 'pH must be between 0 and 14',
            'max_value': 'pH must be between 0 and 14',
            'invalid': 'Please enter a valid number for pH'
        }
    )
    
    n = serializers.FloatField(
        min_value=0,
        required=False,
        allow_null=True,
        help_text="Nitrogen (kg/ha)",
        error_messages={
            'min_value': 'Nitrogen cannot be negative',
            'invalid': 'Please enter a valid number for Nitrogen'
        }
    )
    
    p = serializers.FloatField(
        min_value=0,
        required=False,
        allow_null=True,
        help_text="Phosphorus (kg/ha)",
        error_messages={
            'min_value': 'Phosphorus cannot be negative',
            'invalid': 'Please enter a valid number for Phosphorus'
        }
    )
    
    k = serializers.FloatField(
        min_value=0,
        required=False,
        allow_null=True,
        help_text="Potassium (kg/ha)",
        error_messages={
            'min_value': 'Potassium cannot be negative',
            'invalid': 'Please enter a valid number for Potassium'
        }
    )
    
    def validate_soil_type(self, value):
        """Validate soil type"""
        valid_soils = ['loamy', 'clay', 'sandy', 'silty', 'sandy_loam', 'clay_loam']
        if value and value.lower() not in valid_soils:
            raise serializers.ValidationError(
                f"Invalid soil type. Choose from: {', '.join(valid_soils)}"
            )
        return value.lower() if value else value
    
    def validate_temperature_override(self, value):
        """Validate temperature override"""
        if value is not None:
            if value < -20 or value > 50:
                raise serializers.ValidationError(
                    "Temperature must be between -20°C and 50°C"
                )
        return value
    
    def validate_ph(self, value):
        """Validate pH value"""
        if value is not None:
            if value < 0 or value > 14:
                raise serializers.ValidationError("pH must be between 0 and 14")
            # Warn about extreme pH values
            if value < 4.5:
                raise serializers.ValidationError(
                    "Very acidic soil (pH < 4.5). Most crops will struggle. Consider adding lime."
                )
            if value > 8.5:
                raise serializers.ValidationError(
                    "Very alkaline soil (pH > 8.5). Most crops will struggle. Consider adding sulfur."
                )
        return value
    
    def validate_n(self, value):
        """Validate Nitrogen"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Nitrogen cannot be negative")
            if value > 500:
                raise serializers.ValidationError(
                    "Nitrogen value seems too high (>500 kg/ha). Please verify."
                )
        return value
    
    def validate_p(self, value):
        """Validate Phosphorus"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Phosphorus cannot be negative")
            if value > 300:
                raise serializers.ValidationError(
                    "Phosphorus value seems too high (>300 kg/ha). Please verify."
                )
        return value
    
    def validate_k(self, value):
        """Validate Potassium"""
        if value is not None:
            if value < 0:
                raise serializers.ValidationError("Potassium cannot be negative")
            if value > 500:
                raise serializers.ValidationError(
                    "Potassium value seems too high (>500 kg/ha). Please verify."
                )
        return value
    
    def validate(self, data):
        """Cross-field validations with detailed error messages"""
        errors = {}
        
        # NPK validation - all or nothing
        n = data.get('n')
        p = data.get('p')
        k = data.get('k')
        
        npk_provided = [x for x in [n, p, k] if x is not None]
        
        if npk_provided:
            if len(npk_provided) != 3:
                missing = []
                if n is None:
                    missing.append('Nitrogen (n)')
                if p is None:
                    missing.append('Phosphorus (p)')
                if k is None:
                    missing.append('Potassium (k)')
                
                errors['npk'] = f"For accurate soil analysis, please provide all three NPK values. Missing: {', '.join(missing)}"
        
        # Temperature validation with season
        temp = data.get('temperature_override')
        season = data.get('season')
        region = data.get('region', 'terai')
        
        if temp is not None and season:
            # Check if temperature is realistic for the season
            season_temp_ranges = {
                'spring': (5, 35),
                'monsoon': (15, 40),
                'autumn': (5, 30),
                'winter': (-10, 25)
            }
            min_temp, max_temp = season_temp_ranges.get(season, (-10, 45))
            
            if temp < min_temp or temp > max_temp:
                errors['temperature_override'] = (
                    f"Temperature {temp}°C is unusual for {season} season in {region}. "
                    f"Typical range is {min_temp}°C to {max_temp}°C."
                )
        
        # Region and elevation risk consistency
        elevation_risk = data.get('elevation_risk')
        region = data.get('region', 'terai')
        
        if elevation_risk is True and region == 'terai':
            errors['elevation_risk'] = (
                "Frost risk is set to YES, but you selected TERAI region "
                "which rarely experiences frost. Please verify your inputs."
            )
        
        if elevation_risk is False and region in ['hill', 'mountain']:
            errors['elevation_risk'] = (
                f"Frost risk is set to NO, but you selected {region.upper()} region "
                "which commonly experiences frost. Please verify."
            )
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class CropRecommendationHistorySerializer(serializers.ModelSerializer):
    """Serializer for recommendation history"""
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)
    
    class Meta:
        model = CropRecommendationHistory
        fields = [
            'id', 'farmer', 'farmer_name', 'soil_type', 'ph', 'season',
            'water_availability', 'region', 'temperature', 'frost_risk',
            'experience', 'goal', 'recommendations', 'created_at'
        ]
        read_only_fields = ['farmer', 'created_at']