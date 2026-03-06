from rest_framework import serializers
from .models import AnimalType,Animal


class AnimalTypeSerializer(serializers.ModelSerializer):
    """Serializer for AnimalType"""
    
    class Meta:
        model = AnimalType
        fields = [
            'id','name','name_np',
            'avg_lifespan_years','gestation_days',
            'is_milk_animal','is_egg_animal'
        ]
        
        read_only_fields =['id']
        
        
#---------------Animal Serializers--------------------

class AnimalSerializer(serializers.ModelSerializer):
    """Serializer for individual animals"""
    
    gender_display = serializers.CharField(source='get_gender_display',read_only=True)
    status_display = serializers.CharField(source='get_status_display',read_only=True)
    
    farmer_username = serializers.CharField(source='farmer.username',read_only=True)
    animal_type_name = serializers.CharField(source = 'animal_type.name',read_only=True)
    animal_type_name_np = serializers.CharField(source = 'animal_type.name_np',read_only=True)
    
    
    class Meta:
        model = Animal
        fields =[
             'id', 'farmer', 'farmer_username',
            'animal_type', 'animal_type_name', 'animal_type_name_np',
            'name', 'tag_number',
            'birth_date', 'acquisition_date', 'acquisition_cost',
            'gender', 'gender_display',
            'status', 'status_display',
            'is_pregnant', 'last_pregnancy_date', 'expected_birth_date',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id','created_at','updated_at','farmer']
        
        
        def validate_acquisition_cost(self,value):
            if value < 0:
                raise serializers.ValidationError("Acquistion cost cannot be negative")
            return value
        
        def validate(self,data):
            """Cross-field validation"""
            
            if data.get('is_pregnant') and not data.get('last_pregnancy_date'):
                raise serializers.ValidationError(
                    "Last Pregnancy date is required when animal is pregnant"
                )
                
            if data.get('expected_birth_date') and not data.get('is_pregnant'):
                raise serializers.ValidationError(
                    "Animal must be marked as pregnant to have expected birth date"
                )
                
            if data.get('is_pregnant') and not data.get('gender') != 'female':
                raise serializers.ValidationError(
                    "Only Female animals can be marked as pregnant"
                )
                
            return data