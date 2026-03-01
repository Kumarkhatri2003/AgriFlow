from rest_framework import generics, permissions
from .models import Crop,FertilizerRecord,PesticideRecord
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import (
    CropSerializer,
    FertilizerRecordSerializer,
    PesticideRecordSerializer,
    )

class CropListCreateView(generics.ListCreateAPIView):
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Crop.objects.filter(farmer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

class CropDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific crop"""
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Crop.objects.filter(farmer=self.request.user)
    
    
#--------Fertilizers views------------------

class FertilizerListCreateView(generics.ListCreateAPIView):
    """List all fertilizers or create a new fertilizer record"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
         # Only return fertilizers belonging to the logged-in user

        return FertilizerRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        #get the crop from request data
        crop_id = self.request.data.get('crop')
        
        
        crop = get_object_or_404(Crop,id=crop_id, farmer = self.request.user)
        
        serializer.save(user = self.request.user, crop=crop)
        

class FertilizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get,update or delete a specific fertilizer record"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        # Only return fertilizers belonging to the logged-in user
        
        return FertilizerRecord.objects.filter(user= self.request.user)
    
    def perform_update(self, serializer):
        #if crop is being changed, make sure it belong to user
        
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop,id = crop_id, farmer = self.request.user)
            
        serializer.save()
        
        
        
#-----------------Pesticide Views-------------------

class PesticideListCreateView(generics.ListCreateAPIView):
    """List all pesticides or create a new pesticide record"""
    
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user =self.request.user)
    
    
    def perform_create(self, serializer):
        
        #get the crop from request data
        crop_id = self.request.data.get('crop')
        
        crop = get_object_or_404(Crop, id= crop_id, farmer = self.request.user)
        
        serializer.save(user=self.request.user, crop=crop)
        

class PesticideDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get,update or delete a specific pesticide record"""
    
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)
    
    
    def perform_update(self, serializer):
        # If crop is being changed, make sure it belongs to user
        if 'crop' in self.request.data:
             crop_id =self.request.data.get('crop')
             get_object_or_404(Crop,id=crop_id,farmer = self.request.user)
        serializer.save()
        
        
#-------------------Specific Crop Related data-------------

class CropFertilizersView(generics.ListCreateAPIView):
    """List all fertilizers for specific crop"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        #Get crop_id for URl
        crop_id = self.kwargs['crop_pk']
        
        
        #make sure crop belongs to user
        crop = get_object_or_404(Crop,id=crop_id, farmer=self.request.user)
        
        #Return only fertilizers for this crop
        return FertilizerRecord.objects.filter(crop=crop, user=self.request.user)
    
    
    def perform_create(self, serializer):
        
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop,id=crop_id, farmer=self.request.user)
        
        #save with user and crop
        serializer.save(user=self.request.user, crop=crop)
        

class CropPesticidesView(generics.ListCreateAPIView):
    """List all pesticides for a specific crop"""
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        return PesticideRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)
        