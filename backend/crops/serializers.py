from rest_framework import serializers
from .models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord,Labour,CropKnowledgeBase,CropRecommendationHistory,CropTypeConfig,CropActivityRule
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
            'growth_stage', 'growth_stage_display','growth_stage_manual_override',
            'is_irrigated', 'soil_type',
            'status', 'status_display',
            'notes', 'created_at', 'updated_at',
            
            # Related records
            'fertilizers', 'pesticides', 'expenses', 'incomes', 'harvests','labour_records',
            
            # Financial calculations
            'total_fertilizer_cost', 'total_pesticide_cost', 'total_other_expense',
            'total_expense', 'total_income', 'net_profit', 'total_labor_cost'
        ]
        read_only_fields = ['id', 'farmer', 'created_at', 'updated_at','growth_stage_manual_override']
    
    # ========== ADD THESE VALIDATION METHODS ==========
    
    def update(self, instance, validated_data):
        """Handle manual growth_stage updates with persistent lock"""
        # Detect an explicit user edit to growth_stage
        new_stage = validated_data.pop('growth_stage', None)

        # Update all other fields first
        instance = super().update(instance, validated_data)

        # If growth_stage was provided, lock it permanently
        if new_stage is not None:
            # Even if the value is the same, this still counts as a manual override
            instance.set_manual_growth_stage(new_stage)

        return instance
    
    def validate_name(self, value):
        """
        Validate crop name - allows any valid crop name
        (including custom names not in CropTypeConfig)
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Crop name is required")
        
        if len(value) < 2:
            raise serializers.ValidationError("Crop name must be at least 2 characters")
        
        if len(value) > 100:
            raise serializers.ValidationError("Crop name must be less than 100 characters")
        
        return value.strip()
    
    def validate_variety(self, value):
        """Validate variety - optional field"""
        if value and len(value) > 100:
            raise serializers.ValidationError("Variety name must be less than 100 characters")
        return value
    
    def validate_field_name(self, value):
        """Validate field name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Field name is required")
        
        if len(value) < 2:
            raise serializers.ValidationError("Field name must be at least 2 characters")
        
        if len(value) > 100:
            raise serializers.ValidationError("Field name must be less than 100 characters")
        
        return value.strip()
    
    def validate_field_area(self, value):
        """Validate field area"""
        if value is None:
            raise serializers.ValidationError("Field area is required")
        
        if value <= 0:
            raise serializers.ValidationError("Field area must be greater than 0")
        
        if value > 10000:
            raise serializers.ValidationError("Field area must be less than 10000")
        
        return value
    
    def validate_planting_date(self, value):
        """Validate planting date"""
        from datetime import date
        
        if not value:
            raise serializers.ValidationError("Planting date is required")
        
        if value > date.today():
            raise serializers.ValidationError("Planting date cannot be in the future")
        
        return value
    
    def validate_expected_harvest_date(self, value):
        """Validate expected harvest date"""
        from datetime import date
        
        if value and value < date.today():
            raise serializers.ValidationError("Expected harvest date cannot be in the past")
        
        return value
    
    def validate(self, data):
        """
        Cross-field validation
        """
        # If expected_harvest_date is provided, ensure it's after planting_date
        planting_date = data.get('planting_date')
        expected_harvest_date = data.get('expected_harvest_date')
        
        if planting_date and expected_harvest_date:
            if expected_harvest_date <= planting_date:
                raise serializers.ValidationError({
                    'expected_harvest_date': 'Expected harvest date must be after planting date'
                })
        
        return data


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
    
class CropKnowledgeBaseSerializer(serializers.ModelSerializer):
    """Serializer for the crop knowledge base – matches expert system requirements exactly"""
    
    # Display choices for better UI
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    best_season_display = serializers.CharField(source='get_best_season_display', read_only=True)
    water_req_display = serializers.CharField(source='get_water_req_display', read_only=True)
    drought_tolerance_display = serializers.CharField(source='get_drought_tolerance_display', read_only=True)
    labor_req_display = serializers.CharField(source='get_labor_req_display', read_only=True)
    storage_life_display = serializers.CharField(source='get_storage_life_display', read_only=True)
    frost_sensitive_display = serializers.CharField(source='get_frost_sensitive_display', read_only=True)
    
    # Helper lists (parsed from comma-separated strings)
    all_seasons = serializers.SerializerMethodField()
    regions_suitable = serializers.SerializerMethodField()
    acceptable_soils = serializers.SerializerMethodField()
    other_seasons_list = serializers.SerializerMethodField()
    
    # NPK level fields for UI display
    n_need_level = serializers.SerializerMethodField()
    p_need_level = serializers.SerializerMethodField()
    k_need_level = serializers.SerializerMethodField()
    
    # Calculated ranges for expert system display
    n_need_min_display = serializers.SerializerMethodField()
    n_need_max_display = serializers.SerializerMethodField()
    p_need_min_display = serializers.SerializerMethodField()
    p_need_max_display = serializers.SerializerMethodField()
    k_need_min_display = serializers.SerializerMethodField()
    k_need_max_display = serializers.SerializerMethodField()

    class Meta:
        model = CropKnowledgeBase
        fields = [
            # Basic Info
            'id', 'name_en', 'name_np', 'category', 'category_display',
            
            # Season
            'best_season', 'best_season_display', 'other_seasons', 'other_seasons_list', 'all_seasons',
            
            # Temperature
            'temp_min', 'temp_max', 'temp_ideal',
            
            # Soil - USE soil_other, NOT soil_acceptable
            'soil_ideal', 'soil_other', 'acceptable_soils',
            
            # pH
            'ph_min', 'ph_max', 'ph_ideal',
            
            # Water
            'water_req', 'water_req_display', 'water_logging_tolerance',
            
            # Region
            'region_suitable', 'regions_suitable',
            
            # Tolerances
            'drought_tolerance', 'drought_tolerance_display',
            'frost_sensitive', 'frost_sensitive_display',
            
            # Labor & Storage
            'labor_req', 'labor_req_display',
            'storage_life', 'storage_life_display',
            
            # NPK - Single values
            'n_need', 'p_need', 'k_need',
            
            # NPK Display Levels
            'n_need_level', 'p_need_level', 'k_need_level',
            
            # NPK Calculated Ranges
            'n_need_min_display', 'n_need_max_display',
            'p_need_min_display', 'p_need_max_display',
            'k_need_min_display', 'k_need_max_display',
            
            # Growth
            'growing_days', 'altitude_min', 'altitude_max',
            
            # Day length
            'day_length_sensitive', 'day_length_type',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    # ========== HELPER METHODS ==========
    
    def get_all_seasons(self, obj):
        """Get list of all seasons this crop can grow in"""
        seasons = [obj.best_season]
        if obj.other_seasons:
            other = [s.strip() for s in obj.other_seasons.split(',') if s.strip()]
            seasons.extend(other)
        return list(set(seasons))
    
    def get_other_seasons_list(self, obj):
        """Get other seasons as list"""
        if obj.other_seasons:
            return [s.strip() for s in obj.other_seasons.split(',') if s.strip()]
        return []
    
    def get_regions_suitable(self, obj):
        """Get suitable regions as list"""
        if obj.region_suitable:
            return [r.strip().lower() for r in obj.region_suitable.split(',') if r.strip()]
        return []
    
    def get_acceptable_soils(self, obj):
        """Get acceptable soils as list - uses soil_other field"""
        if obj.soil_other:
            return [s.strip() for s in obj.soil_other.split(',') if s.strip()]
        return []
    
    # ========== NPK LEVEL METHODS ==========
    
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
    
    # ========== NPK RANGE METHODS ==========
    
    def get_n_need_min_display(self, obj):
        return max(20, obj.n_need * 0.6)
    
    def get_n_need_max_display(self, obj):
        return obj.n_need * 1.4
    
    def get_p_need_min_display(self, obj):
        return max(10, obj.p_need * 0.6)
    
    def get_p_need_max_display(self, obj):
        return obj.p_need * 1.4
    
    def get_k_need_min_display(self, obj):
        return max(10, obj.k_need * 0.6)
    
    def get_k_need_max_display(self, obj):
        return obj.k_need * 1.4




class CropRecommendationRequestSerializer(serializers.Serializer):
    """
    Serializer for crop recommendation requests
    Matches exactly what expert system expects
    """
    
    # ========== REQUIRED FIELDS ==========
    
    region = serializers.ChoiceField(
        choices=['terai', 'mid-hill', 'hill', 'mountain'],
        required=True,
        error_messages={
            'required': 'Region is required',
            'invalid_choice': 'Invalid region. Choose from: terai, mid-hill, hill, mountain'
        }
    )
    
    season = serializers.ChoiceField(
        choices=['spring', 'summer', 'monsoon', 'autumn', 'winter'],
        required=True,
        error_messages={
            'required': 'Season is required',
            'invalid_choice': 'Invalid season. Choose from: spring, summer, monsoon, autumn, winter'
        }
    )
    
    water_source = serializers.ChoiceField(
        choices=['rainfed_only', 'canal', 'well', 'river', 'drip_irrigation'],
        required=True,
        error_messages={
            'required': 'Water source is required',
            'invalid_choice': 'Invalid water source. Choose from: rainfed_only, canal, well, river, drip_irrigation'
        }
    )
    
    soil_type = serializers.ChoiceField(
        choices=['clay', 'loamy', 'sandy', 'silty', 'clay_loam'],
        required=True,
        error_messages={
            'required': 'Soil type is required',
            'invalid_choice': 'Invalid soil type. Choose from: clay, loamy, sandy, silty, clay_loam'
        }
    )
    
    labor_availability = serializers.ChoiceField(
        choices=['low', 'medium', 'high'],
        required=True,
        error_messages={
            'required': 'Labor availability is required',
            'invalid_choice': 'Invalid labor availability. Choose from: low, medium, high'
        }
    )
    
    market_distance = serializers.ChoiceField(
        choices=['near', 'medium', 'far'],
        required=True,
        error_messages={
            'required': 'Market distance is required',
            'invalid_choice': 'Invalid market distance. Choose from: near, medium, far'
        }
    )
    
    farming_goal = serializers.ChoiceField(
        choices=['profit', 'food_security', 'mixed', 'subsistence'],
        required=True,
        error_messages={
            'required': 'Farming goal is required',
            'invalid_choice': 'Invalid farming goal. Choose from: profit, food_security, mixed, subsistence'
        }
    )
    
    # ========== NEW REQUIRED FIELDS ==========
    
    temperature = serializers.FloatField(
        required=True,
        min_value=-20,
        max_value=50,
        error_messages={
            'required': 'Temperature is required',
            'min_value': 'Temperature must be between -20°C and 50°C',
            'max_value': 'Temperature must be between -20°C and 50°C',
            'invalid': 'Please enter a valid number for temperature'
        }
    )
    
    frost_risk = serializers.ChoiceField(
        choices=['yes', 'no'],
        required=True,
        error_messages={
            'required': 'Frost risk is required',
            'invalid_choice': 'Invalid choice. Choose from: yes, no'
        }
    )
    
    drought_risk = serializers.ChoiceField(
        choices=['high', 'medium', 'low'],
        required=True,
        help_text="Drought risk level at your farm location",
        error_messages={
            'required': 'Drought risk is required',
            'invalid_choice': 'Invalid choice. Choose from: high, medium, low'
        }
    )
    
    # ========== OPTIONAL FIELDS (Hidden by default) ==========
    
    ph = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=14,
        error_messages={
            'min_value': 'pH must be between 0 and 14',
            'max_value': 'pH must be between 0 and 14',
            'invalid': 'Please enter a valid number for pH'
        }
    )
    
    n = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=500,
        error_messages={
            'min_value': 'Nitrogen cannot be negative',
            'max_value': 'Nitrogen seems too high (>500 kg/ha)',
            'invalid': 'Please enter a valid number for Nitrogen'
        }
    )
    
    p = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=300,
        error_messages={
            'min_value': 'Phosphorus cannot be negative',
            'max_value': 'Phosphorus seems too high (>300 kg/ha)',
            'invalid': 'Please enter a valid number for Phosphorus'
        }
    )
    
    k = serializers.FloatField(
        required=False,
        allow_null=True,
        min_value=0,
        max_value=500,
        error_messages={
            'min_value': 'Potassium cannot be negative',
            'max_value': 'Potassium seems too high (>500 kg/ha)',
            'invalid': 'Please enter a valid number for Potassium'
        }
    )
    
    # Backward compatibility fields
    temperature_override = serializers.FloatField(required=False, allow_null=True, write_only=True)
    elevation_risk = serializers.BooleanField(required=False, allow_null=True, write_only=True)
    
    def validate(self, data):
        """Cross-field validations"""
        errors = {}
        
        # Convert backward compatibility fields
        if 'temperature_override' in data and data['temperature_override'] is not None:
            if 'temperature' not in data or data['temperature'] is None:
                data['temperature'] = data['temperature_override']
        
        if 'elevation_risk' in data and data['elevation_risk'] is not None:
            if 'frost_risk' not in data or data['frost_risk'] is None:
                data['frost_risk'] = 'yes' if data['elevation_risk'] else 'no'
        
        # NPK validation - all or nothing warning (not error)
        n = data.get('n')
        p = data.get('p')
        k = data.get('k')
        
        npk_provided = [x for x in [n, p, k] if x is not None]
        
        if npk_provided and len(npk_provided) != 3:
            # This is a warning, not an error
            missing = []
            if n is None:
                missing.append('Nitrogen (n)')
            if p is None:
                missing.append('Phosphorus (p)')
            if k is None:
                missing.append('Potassium (k)')
            # Add warning to data for frontend
            data['_npk_warning'] = f"For accurate soil analysis, please provide all three NPK values. Missing: {', '.join(missing)}"
        
        # Region and frost risk consistency (warning only)
        region = data.get('region')
        frost_risk = data.get('frost_risk')
        
        if region == 'terai' and frost_risk == 'yes':
            data['_frost_warning'] = "Terai region rarely experiences frost. Please verify your input."
        
        if region in ['hill', 'mountain'] and frost_risk == 'no':
            data['_frost_warning'] = f"{region.upper()} region commonly experiences frost. Please verify."
        
        # Temperature and season consistency (warning only)
        temperature = data.get('temperature')
        season = data.get('season')
        
        if temperature and season:
            season_temp_ranges = {
                'spring': (5, 35),
                'summer': (15, 40),
                'monsoon': (15, 40),
                'autumn': (5, 30),
                'winter': (-10, 25)
            }
            min_temp, max_temp = season_temp_ranges.get(season, (-10, 45))
            
            if temperature < min_temp or temperature > max_temp:
                data['_temp_warning'] = (
                    f"Temperature {temperature}°C is unusual for {season} season in {region}. "
                    f"Typical range is {min_temp}°C to {max_temp}°C."
                )
        
        return data
    
    def to_representation(self, instance):
        """Custom representation to include warnings"""
        representation = super().to_representation(instance)
        
        # Add warnings if they exist
        if hasattr(instance, '_npk_warning'):
            representation['_npk_warning'] = instance._npk_warning
        if hasattr(instance, '_frost_warning'):
            representation['_frost_warning'] = instance._frost_warning
        if hasattr(instance, '_temp_warning'):
            representation['_temp_warning'] = instance._temp_warning
        
        return representation


class CropRecommendationHistorySerializer(serializers.ModelSerializer):
    """Serializer for recommendation history"""
    
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)
    
    # Display values for choices
    region_display = serializers.SerializerMethodField()
    season_display = serializers.SerializerMethodField()
    water_source_display = serializers.SerializerMethodField()
    soil_type_display = serializers.SerializerMethodField()
    labor_availability_display = serializers.SerializerMethodField()
    market_distance_display = serializers.SerializerMethodField()
    farming_goal_display = serializers.SerializerMethodField()
    frost_risk_display = serializers.SerializerMethodField()
    drought_risk_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CropRecommendationHistory
        fields = [
            'id', 'farmer', 'farmer_name',
            'region', 'region_display',
            'season', 'season_display',
            'water_source', 'water_source_display',
            'soil_type', 'soil_type_display',
            'labor_availability', 'labor_availability_display',
            'market_distance', 'market_distance_display',
            'farming_goal', 'farming_goal_display',
            'temperature', 'frost_risk', 'frost_risk_display',
            'drought_risk', 'drought_risk_display',
            'ph', 'n', 'p', 'k',
            'recommendations', 'created_at'
        ]
        read_only_fields = ['farmer', 'created_at']
    
    def get_region_display(self, obj):
        """Get region display value"""
        region_map = {
            'terai': 'Terai',
            'mid-hill': 'Mid-Hill',
            'hill': 'Hill',
            'mountain': 'Mountain'
        }
        return region_map.get(obj.region, obj.region)
    
    def get_season_display(self, obj):
        """Get season display value"""
        season_map = {
            'spring': 'Spring',
            'summer': 'Summer',
            'monsoon': 'Monsoon',
            'autumn': 'Autumn',
            'winter': 'Winter'
        }
        return season_map.get(obj.season, obj.season)
    
    def get_water_source_display(self, obj):
        """Get water source display value"""
        water_map = {
            'rainfed_only': 'Rainfed Only',
            'canal': 'Canal',
            'well': 'Well',
            'river': 'River',
            'drip_irrigation': 'Drip Irrigation'
        }
        return water_map.get(obj.water_source, obj.water_source)
    
    def get_soil_type_display(self, obj):
        """Get soil type display value"""
        soil_map = {
            'clay': 'Clay',
            'loamy': 'Loamy',
            'sandy': 'Sandy',
            'silty': 'Silty',
            'clay_loam': 'Clay Loam'
        }
        return soil_map.get(obj.soil_type, obj.soil_type)
    
    def get_labor_availability_display(self, obj):
        """Get labor availability display value"""
        labor_map = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High'
        }
        return labor_map.get(obj.labor_availability, obj.labor_availability)
    
    def get_market_distance_display(self, obj):
        """Get market distance display value"""
        market_map = {
            'near': 'Near',
            'medium': 'Medium',
            'far': 'Far'
        }
        return market_map.get(obj.market_distance, obj.market_distance)
    
    def get_farming_goal_display(self, obj):
        """Get farming goal display value"""
        goal_map = {
            'profit': 'Profit',
            'food_security': 'Food Security',
            'mixed': 'Mixed',
            'subsistence': 'Subsistence'
        }
        return goal_map.get(obj.farming_goal, obj.farming_goal)
    
    def get_frost_risk_display(self, obj):
        """Get frost risk display value"""
        return 'Yes' if obj.frost_risk else 'No'
    
    def get_drought_risk_display(self, obj):
        """Get drought risk display value"""
        risk_map = {
            'high': 'High Risk',
            'medium': 'Medium Risk',
            'low': 'Low Risk'
        }
        return risk_map.get(obj.drought_risk, obj.drought_risk)
    
    def validate_recommendations(self, value):
        """Validate recommendations JSON structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Recommendations must be a JSON object")
        if 'recommendations' not in value:
            raise serializers.ValidationError("Recommendations must contain 'recommendations' key")
        return value
        
class CropTypeConfigSerializer(serializers.ModelSerializer):
    """Serializer for CropTypeConfig with computed display fields"""
    
    display_name = serializers.SerializerMethodField()
    region_display = serializers.SerializerMethodField()
    season_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CropTypeConfig
        fields = [
            'id', 'crop_name', 'variety', 'region', 'region_display',
            'season', 'season_display', 'display_name',
            'germination_start_day', 'germination_end_day',
            'vegetative_start_day', 'vegetative_end_day',
            'flowering_start_day', 'flowering_end_day',
            'maturation_start_day', 'maturation_end_day',
            'harvest_start_day', 'harvest_end_day',
            'total_growing_days', 'is_active'
        ]
        
        def get_display_name(self, obj):
            return obj.get_display_name()
    
        def get_region_display(self, obj):
            return obj.get_region_display()
    
        def get_season_display(self, obj):
            return obj.get_season_display()
        

class CropActivityRuleSerializer(serializers.ModelSerializer):
    """Serializer for CropActivityRule with nested config details"""
    
    crop_config_details = CropTypeConfigSerializer(source='crop_config', read_only=True)
    growth_stage_display = serializers.SerializerMethodField()
    
    class Meta:
        model = CropActivityRule
        fields = [
            'id', 'crop_config', 'crop_config_details',
            'growth_stage', 'growth_stage_display',
            'title', 'title_np', 'description', 'description_np',
            'measurements', 'target_pest', 'recommendations',
            'day_offset', 'order', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
        
    def get_growth_stage_display(self, obj):
        return obj.get_growth_stage_display()

