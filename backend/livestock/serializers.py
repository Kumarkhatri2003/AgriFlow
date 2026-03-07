from rest_framework import serializers
from .models import AnimalType,Animal,VaccinationRecord,HealthRecord


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
                
class VaccinationRecordSerializer(serializers.ModelSerializer):
    """Serializer for vaccination records"""
    animal_name = serializers.CharField(source='animal.name',read_only = True)
    animal_tag = serializers.CharField(source = 'animal.tag_number', read_only = True)
    
    class Meta:
        model = VaccinationRecord
        fields = [
            'id', 'animal', 'animal_name', 'animal_tag',
            'vaccine_name', 'vaccine_date', 'next_due_date',
            'administered_by', 'cost', 'notes', 'created_at' 
        ]
        
        read_only_fields = ['id', 'created_at']
        
    def validate_cost(self, value):
        
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value



class HealthRecordSerializer(serializers.ModelSerializer):
    """Serializer for health records"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    health_type_display = serializers.CharField(source='get_health_type_display', read_only=True)
    
    class Meta:
        model = HealthRecord
        fields = [
            'id', 'animal', 'animal_name', 'animal_tag',
            'health_type', 'health_type_display',
            'diagnosis', 'treatment', 'treatment_date', 'follow_up_date',
            'vet_name', 'cost', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value


class AnimalSerializer(serializers.ModelSerializer):
    """Serializer for animals with nested records"""
    
    # Display fields
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Related data
    farmer_username = serializers.CharField(source='farmer.username', read_only=True)
    animal_type_name = serializers.CharField(source='animal_type.name', read_only=True)
    animal_type_name_np = serializers.CharField(source='animal_type.name_np', read_only=True)
    
    # Nested records (read-only)
    vaccinations = VaccinationRecordSerializer(many=True, read_only=True)
    health_records = HealthRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Animal
        fields = [
            'id', 'farmer', 'farmer_username',
            'animal_type', 'animal_type_name', 'animal_type_name_np',
            'name', 'tag_number',
            'birth_date', 'acquisition_date', 'acquisition_cost',
            'gender', 'gender_display',
            'status', 'status_display',
            'is_pregnant', 'last_pregnancy_date', 'expected_birth_date',
            'notes', 'created_at', 'updated_at',
            'vaccinations', 'health_records'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'farmer']
    
    def validate_acquisition_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Acquisition cost cannot be negative")
        return value
    
    def validate(self, data):
        if data.get('is_pregnant') and not data.get('last_pregnancy_date'):
            raise serializers.ValidationError(
                "Last pregnancy date is required when animal is pregnant"
            )
        if data.get('expected_birth_date') and not data.get('is_pregnant'):
            raise serializers.ValidationError(
                "Animal must be marked as pregnant to have expected birth date"
            )
        if data.get('is_pregnant') and data.get('gender') != 'female':
            raise serializers.ValidationError(
                "Only female animals can be marked as pregnant"
            )
        return data
    