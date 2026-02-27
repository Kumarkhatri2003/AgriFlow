from rest_framework import serializers
from .models import Crop


class CropSerializer(serializers.ModelSerializer):
    """serializer for crop model"""

     # Show farmer's username instead of ID
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    
    # Human-readable versions of choice fields
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    irrigation_type_display = serializers.CharField(source='get_irrigation_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    area_unit_display = serializers.CharField(source='get_area_unit_display', read_only=True)


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
            'notes', 'created_at'
        ]

        read_only_fields = ['id','created_at','farmer']