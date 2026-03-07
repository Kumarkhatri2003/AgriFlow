from rest_framework import generics,permissions,status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AnimalType, Animal,HealthRecord,VaccinationRecord
from .serializers import (
    AnimalTypeSerializer,
    AnimalSerializer,
    VaccinationRecordSerializer,
    HealthRecordSerializer,
)


# Create your views here.
class AnimalTypeListView(generics.ListAPIView):
    """List all animal types(for dropdowm menus)"""
    
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    

class AnimalTypeDetailView(generics.RetrieveAPIView):
    """Get details of a specific animal type"""
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
#------------------Animal Views (Full CRUD for farmers)-------------------
class AnimalListCreateView(generics.ListCreateAPIView):
    """List all animals or create a new animal"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return animals belongings to the logged-in user
        return Animal.objects.filter(farmer=self.request.user)
    
    def perform_create(self, serializer):
        #Automatically set the farmer to the logged-in user
        serializer.save(farmer = self.request.user)
        

class AnimalDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get,update or delete a specific animal"""
    
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Animal.objects.filter(farmer = self.request.user)
    
    def perform_update(self, serializer):
        #If  animal_type is being changed, make sure it exists
        if 'animal_type' in self.request.data:
            animal_type_id = self.request.data.get('animal_type')
            get_object_or_404(AnimalType, id=animal_type_id)
            
        
        #save the updated records   
        serializer.save()
        
        
#------------Filtered Views-----------------------

class AnimalByTypeView(generics.ListAPIView):
    """List animals filtered by animal type"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        animal_type_id = self.kwargs['type_id']
        
        get_object_or_404(AnimalType, id=animal_type_id)
        
        return Animal.objects.filter(
            farmer = self.request.user,
            animal_type_id = animal_type_id
        )
        

class PregnantAnimalView(generics.ListAPIView):
    """List all pregnant animals"""
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        return Animal.objects.filter(
            farmer = self.request.user,
            is_pregnant = True
        )
        
class ActiveAnimalsView(generics.ListAPIView):
    """List all the active animals"""
    
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
        # Return vaccinations for animals belonging to the user
        return VaccinationRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        # Make sure the animal belongs to the user
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class VaccinationRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific vaccination record"""
    serializer_class = VaccinationRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return vaccinations for user's animals
        return VaccinationRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        # If animal is being changed, make sure it belongs to user
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
        # Return health records for animals belonging to the user
        return HealthRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_create(self, serializer):
        # Make sure the animal belongs to the user
        animal_id = self.request.data.get('animal')
        animal = get_object_or_404(Animal, id=animal_id, farmer=self.request.user)
        serializer.save(animal=animal)


class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific health record"""
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only return health records for user's animals
        return HealthRecord.objects.filter(animal__farmer=self.request.user)
    
    def perform_update(self, serializer):
        # If animal is being changed, make sure it belongs to user
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
        # Make sure animal belongs to user
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
    