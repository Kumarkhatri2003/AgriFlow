# crops/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord
)
from .serializers import (
    CropSerializer,
    FertilizerRecordSerializer,
    PesticideRecordSerializer,
    CropExpenseSerializer,
    CropIncomeSerializer,
    HarvestRecordSerializer
)
import uuid

# ==================== MAIN CROP VIEWS ====================

class CropListCreateView(generics.ListCreateAPIView):
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Crop.objects.filter(farmer=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)


class CropDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Crop.objects.filter(farmer=self.request.user)


# ==================== FERTILIZER VIEWS ====================

class FertilizerListCreateView(generics.ListCreateAPIView):
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        # Handle UUID string
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class FertilizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)


# ==================== PESTICIDE VIEWS ====================

class PesticideListCreateView(generics.ListCreateAPIView):
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class PesticideDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)


# ==================== CROP EXPENSE VIEWS ====================

class CropExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropExpense.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropExpense.objects.filter(user=self.request.user)


# ==================== CROP INCOME VIEWS ====================

class CropIncomeListCreateView(generics.ListCreateAPIView):
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropIncome.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropIncomeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropIncome.objects.filter(user=self.request.user)


# ==================== HARVEST RECORD VIEWS ====================

class HarvestRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HarvestRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class HarvestRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HarvestRecord.objects.filter(user=self.request.user)


# ==================== NESTED VIEWS (UNDER SPECIFIC CROP) ====================

class CropFertilizersView(generics.ListCreateAPIView):
    """List all fertilizers for specific crop"""
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        # Convert string to UUID if needed
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return FertilizerRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropPesticidesView(generics.ListCreateAPIView):
    """List all pesticides for a specific crop"""
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return PesticideRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropExpensesView(generics.ListCreateAPIView):
    """List all expenses for a specific crop"""
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return CropExpense.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropIncomesView(generics.ListCreateAPIView):
    """List all incomes for a specific crop"""
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return CropIncome.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropHarvestsView(generics.ListCreateAPIView):
    """List all harvests for a specific crop"""
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return HarvestRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)