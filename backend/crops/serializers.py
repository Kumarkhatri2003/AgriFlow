from rest_framework import serializers
from .models import Crop,FertilizerRecord,PesticideRecord

#--------Fertilizer Serializer----------------    
class FertilizerRecordSerializer(serializers.ModelSerializer):
    """Serializer for fertilizer records"""
    
    #show human-readable names
    fertilizer_type_display = serializers.CharField(
    source='get_fertilizer_type_display',
    read_only=True
    )
    unit_display = serializers.CharField(source='get_unit_display',read_only=True)
    
    #crop name and user info
    crop_name = serializers.CharField(source ='crop.name',read_only=True)
    user_username = serializers.CharField(source ='user.username',read_only = True)
    
    class Meta:
        model = FertilizerRecord
        fields= [
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'fertilizer_type', 'fertilizer_type_display', 'name',
            'quantity', 'unit', 'unit_display', 'cost',
            'application_date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_quantity(self, value):
        print(f"🔍 Validating quantity: {value}")  # Add this for debugging
        if float(value) < 0:  # Convert to float for comparison
            raise serializers.ValidationError("Quantity cannot be negative")
        return value
    
    def validate_cost(self, value):
        print(f"🔍 Validating cost: {value}")  # Add this for debugging
        if float(value) < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value
    
        
    
#--------Pesticide Serializer----------------    
class PesticideRecordSerializer(serializers.ModelSerializer):
    """Simple serializer for pesticide records"""
    
    unit_display = serializers.CharField(source='get_unit_display',read_only=True)

    crop_name= serializers.CharField(source='crop.name',read_only=True)
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    
    class Meta:
        model = PesticideRecord
        fields =[
            'id', 'user', 'user_username', 'crop', 'crop_name',
            'name', 'target_pest',
            'quantity', 'unit', 'unit_display', 'cost',
            'application_date', 'notes', 'created_at'  
        ]
        
        read_only_fields = ['id','user','created_at']
        
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value 
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value
    
class CropSerializer(serializers.ModelSerializer):
    """serializer for crop model"""

     # Show farmer's username instead of ID
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    # Human-readable versions of choice fields
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    irrigation_type_display = serializers.CharField(source='get_irrigation_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    area_unit_display = serializers.CharField(source='get_area_unit_display', read_only=True)

    fertilizers = FertilizerRecordSerializer(many=True, read_only= True)
    pesticides = PesticideRecordSerializer(many=True,read_only=True)
    
    class Meta:
        model = Crop
        fields = [
            'id', 'farmer', 'farmer_username',
            'name', 'name_np', 'variety',
            'field_name', 'field_area', 'area_unit', 'area_unit_display',
            'planting_date', 'expected_harvest_date',
            'growth_stage', 'growth_stage_display',
            'irrigation_type', 'irrigation_type_display',
            'soil_type', 'status', 'status_display',
            'notes', 'created_at',
            'fertilizers','pesticides'
        ]

        read_only_fields = ['id','created_at','farmer','fertilizers','pesticides']
        

        
