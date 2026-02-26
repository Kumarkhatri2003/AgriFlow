from rest_framework import generics, permissions
from .models import Crop
from .serializers import CropSerializer

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