from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AnimalType, Animal, HealthRecord, VaccinationRecord, MilkRecord, BreedingRecord
from .serializers import (
    AnimalTypeSerializer,
    AnimalSerializer,
    VaccinationRecordSerializer,
    HealthRecordSerializer,
    MilkRecordSerializer, 
    BreedingRecordSerializer,  
)


# ==================== ANIMAL TYPE VIEWS ====================
class AnimalTypeListView(generics.ListAPIView):
    """List all animal types (for dropdown menus)"""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class AnimalTypeDetailView(generics.RetrieveAPIView):
    """Get details of a specific animal type"""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


# ==================== ANIMAL VIEWS ====================
class AnimalListCreateView(generics.ListCreateAPIView):
    """List all animals or create a new animal"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Animal.objects.filter(farmer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)


class AnimalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific animal"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Animal.objects.filter(farmer=self.request.user)
    
    def perform_update(self, serializer):
        if 'animal_type' in self.request.data:
            animal_type_id = self.request.data.get('animal_type')
            get_object_or_404(AnimalType, id=animal_type_id)
        serializer.save()


# ==================== FILTERED ANIMAL VIEWS ====================
class AnimalByTypeView(generics.ListAPIView):
    """List animals filtered by animal type"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_type_id = self.kwargs['type_id']
        get_object_or_404(AnimalType, id=animal_type_id)
        return Animal.objects.filter(
            farmer=self.request.user,
            animal_type_id=animal_type_id
        )


class PregnantAnimalView(generics.ListAPIView):
    """List all pregnant animals"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Animal.objects.filter(
            farmer=self.request.user,
            is_pregnant=True
        )


class ActiveAnimalsView(generics.ListAPIView):
    """List all active animals"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Animal.objects.filter(
            farmer=self.request.user,
            status='active'
        )


# ==================== VACCINATION RECORD VIEWS ====================
class VaccinationRecordListCreateView(generics.ListCreateAPIView):
    """List all vaccinations or create a new vaccination record"""
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VaccinationRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class VaccinationRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific vaccination record"""
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return VaccinationRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        if 'animal' in self.request.data:
            animal_id = self.request.data.get('animal')
            get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save()


# ==================== HEALTH RECORD VIEWS ====================
class HealthRecordListCreateView(generics.ListCreateAPIView):
    """List all health records or create a new health record"""
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific health record"""
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HealthRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        if 'animal' in self.request.data:
            animal_id = self.request.data.get('animal')
            get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save()


# ==================== MILK RECORD VIEWS ====================
class MilkRecordListCreateView(generics.ListCreateAPIView):
    """List all milk records or create a new milk record"""
    serializer_class = MilkRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MilkRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class MilkRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific milk record"""
    serializer_class = MilkRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MilkRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        if 'animal' in self.request.data:
            animal_id = self.request.data.get('animal')
            get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save()


# ==================== BREEDING RECORD VIEWS ====================
class BreedingRecordListCreateView(generics.ListCreateAPIView):
    """List all breeding records or create a new breeding record"""
    serializer_class = BreedingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BreedingRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class BreedingRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific breeding record"""
    serializer_class = BreedingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return BreedingRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        if 'animal' in self.request.data:
            animal_id = self.request.data.get('animal')
            get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save()


# ==================== NESTED VIEWS (UNDER SPECIFIC ANIMAL) ====================

class AnimalVaccinationsView(generics.ListCreateAPIView):
    """List all vaccinations for a specific animal"""
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        return VaccinationRecord.objects.filter(animal=animal)
    
    def perform_create(self, serializer):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class AnimalHealthRecordsView(generics.ListCreateAPIView):
    """List all health records for a specific animal"""
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        return HealthRecord.objects.filter(animal=animal)
    
    def perform_create(self, serializer):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class AnimalMilkRecordsView(generics.ListCreateAPIView):
    """List all milk records for a specific animal"""
    serializer_class = MilkRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        return MilkRecord.objects.filter(animal=animal)
    
    def perform_create(self, serializer):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class AnimalBreedingRecordsView(generics.ListCreateAPIView):
    """List all breeding records for a specific animal (as mother)"""
    serializer_class = BreedingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        return BreedingRecord.objects.filter(animal=animal)
    
    def perform_create(self, serializer):
        animal_id = self.kwargs['animal_pk']
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)