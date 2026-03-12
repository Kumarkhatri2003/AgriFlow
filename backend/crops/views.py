from rest_framework import generics, permissions
from .models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord
)
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import (
    CropSerializer,
    FertilizerRecordSerializer,
    PesticideRecordSerializer,
    CropExpenseSerializer,
    CropIncomeSerializer,
    HarvestRecordSerializer
)


# ==================== MAIN CROP VIEWS ====================

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


# ==================== FERTILIZER VIEWS ====================

class FertilizerListCreateView(generics.ListCreateAPIView):
    """List all fertilizers or create a new fertilizer record"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class FertilizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific fertilizer record"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save()


# ==================== PESTICIDE VIEWS ====================

class PesticideListCreateView(generics.ListCreateAPIView):
    """List all pesticides or create a new pesticide record"""
    
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class PesticideDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific pesticide record"""
    
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save()


# ==================== CROP EXPENSE VIEWS ====================

class CropExpenseListCreateView(generics.ListCreateAPIView):
    """List all crop expenses or create a new expense"""
    
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropExpense.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific crop expense"""
    
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropExpense.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save()


# ==================== CROP INCOME VIEWS ====================

class CropIncomeListCreateView(generics.ListCreateAPIView):
    """List all crop incomes or create a new income"""
    
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropIncome.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropIncomeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific crop income"""
    
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropIncome.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save()


# ==================== HARVEST RECORD VIEWS ====================

class HarvestRecordListCreateView(generics.ListCreateAPIView):
    """List all harvest records or create a new harvest record"""
    
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HarvestRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class HarvestRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific harvest record"""
    
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HarvestRecord.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        if 'crop' in self.request.data:
            crop_id = self.request.data.get('crop')
            get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save()


# ==================== NESTED VIEWS (UNDER SPECIFIC CROP) ====================

class CropFertilizersView(generics.ListCreateAPIView):
    """List all fertilizers for specific crop"""
    
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        return FertilizerRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
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


class CropExpensesView(generics.ListCreateAPIView):
    """List all expenses for a specific crop"""
    
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        return CropExpense.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropIncomesView(generics.ListCreateAPIView):
    """List all incomes for a specific crop"""
    
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        return CropIncome.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class CropHarvestsView(generics.ListCreateAPIView):
    """List all harvests for a specific crop"""
    
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        return HarvestRecord.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.kwargs['crop_pk']
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)