from rest_framework import serializers
from .models import AnimalType,Animal,VaccinationRecord,HealthRecord,MilkRecord,BreedingRecord


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


#-----------------------Milk Record Serializers --------------------
class MilkRecordSerializer(serializers.ModelSerializer):
    """serializer for milk production records"""
    
    animal_name = serializers.CharField(source='animal.name',read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only = True)
    milk_time_display = serializers.CharField(source = 'get_milk_time_display',read_only = True)
    
    class Meta:
        model = MilkRecord
        fields = [
            'id','animal','animal_name','animal_tag',
            'date','quantity_liters','milk_time','milk_time_display',
            'notes','created_at'
        ]
        
        read_only_fields =['id','created_at']
        
        def validate_quantity_liters(self,value):
            if value < 0:
                raise serializers.ValidationError("Quantity cannot be negative")
            return value
        
        
#------------------Breeding Record Serializer---------------------
class BreedingRecordSerializer(serializers.ModelSerializer):
    """Serializer for breeding records"""
    
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    animal_tag = serializers.CharField(source='animal.tag_number', read_only=True)
    sire_name_display = serializers.SerializerMethodField()
    
    class Meta:
        model = BreedingRecord
        fields = [
            'id', 'animal', 'animal_name', 'animal_tag',
            'breeding_date', 'successful',
            'expected_birth_date', 'actual_birth_date', 'offspring_count',
            'sire_animal', 'sire_name', 'sire_name_display',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_sire_name_display(self, obj):
        """Return the sire name (either from sire_animal or sire_name)"""
        if obj.sire_animal:
            return f"{obj.sire_animal.name or 'Unnamed'} ({obj.sire_animal.tag_number})"
        return obj.sire_name or "Unknown"
    
    def validate_offspring_count(self, value):
        if value < 0:
            raise serializers.ValidationError("Offspring count cannot be negative")
        return value
    
    def validate(self, data):
        successful = data.get('successful', False)
        
        # If breeding was not successful, clear any birth-related fields
        if not successful:
            if data.get('expected_birth_date'):
                raise serializers.ValidationError(
                    "Cannot have expected birth date for unsuccessful breeding"
                )
            if data.get('actual_birth_date'):
                raise serializers.ValidationError(
                    "Cannot have actual birth date for unsuccessful breeding"
                )
            if data.get('offspring_count', 0) > 0:
                raise serializers.ValidationError(
                    "Cannot have offspring count for unsuccessful breeding"
                )
            return data
        
        # For successful breeding
        # Case 1: Breeding just happened (no actual birth yet)
        if not data.get('actual_birth_date'):
            if not data.get('expected_birth_date'):
                raise serializers.ValidationError(
                    "Expected birth date is required for successful breeding"
                )
            if data.get('offspring_count', 0) > 0:
                raise serializers.ValidationError(
                    "Offspring count cannot be set until birth occurs"
                )
        
        # Case 2: Birth has occurred
        if data.get('actual_birth_date'):
            if not data.get('offspring_count', 0) > 0:
                raise serializers.ValidationError(
                    "Offspring count is required when birth date is recorded"
                )
        
        return data
                
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
    milk_records = MilkRecordSerializer(many=True,read_only=True)
    breeding_records = BreedingRecordSerializer(many=True,read_only=True)
    
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
            'vaccinations', 'health_records','milk_records','breeding_records'
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
    