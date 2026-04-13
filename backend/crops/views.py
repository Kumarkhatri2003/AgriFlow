from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .expert_system import get_recommendations
from .models import (
    Crop, CropRecommendationHistory, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord, Labour,CropKnowledgeBase
)

from .serializers import (
    CropRecommendationHistorySerializer,
    CropRecommendationRequestSerializer,
    CropSerializer,
    FertilizerRecordSerializer,
    FertilizerRecordCreateSerializer,
    PesticideRecordSerializer,
    PesticideRecordCreateSerializer,
    CropExpenseSerializer,
    CropExpenseCreateSerializer,
    CropIncomeSerializer,
    CropIncomeCreateSerializer,
    HarvestRecordSerializer,
    HarvestRecordCreateSerializer,
    LaborSerializer,
    LaborCreateSerializer,

)
import uuid

# ==================== MAIN CROP VIEWS ====================

class CropListCreateView(generics.ListCreateAPIView):
    """List all crops or create a new crop"""
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
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FertilizerRecordCreateSerializer
        return FertilizerRecordSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class FertilizerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific fertilizer record"""
    serializer_class = FertilizerRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return FertilizerRecord.objects.filter(user=self.request.user)


# ==================== PESTICIDE VIEWS ====================

class PesticideListCreateView(generics.ListCreateAPIView):
    """List all pesticides or create a new pesticide record"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PesticideRecordCreateSerializer
        return PesticideRecordSerializer
    
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
    """Get, update or delete a specific pesticide record"""
    serializer_class = PesticideRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PesticideRecord.objects.filter(user=self.request.user)


# ==================== CROP EXPENSE VIEWS ====================

class CropExpenseListCreateView(generics.ListCreateAPIView):
    """List all crop expenses or create a new expense"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CropExpenseCreateSerializer
        return CropExpenseSerializer
    
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
    """Get, update or delete a specific crop expense"""
    serializer_class = CropExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropExpense.objects.filter(user=self.request.user)


# ==================== CROP INCOME VIEWS ====================

class CropIncomeListCreateView(generics.ListCreateAPIView):
    """List all crop incomes or create a new income"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CropIncomeCreateSerializer
        return CropIncomeSerializer
    
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
    """Get, update or delete a specific crop income"""
    serializer_class = CropIncomeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CropIncome.objects.filter(user=self.request.user)


# ==================== HARVEST RECORD VIEWS ====================

class HarvestRecordListCreateView(generics.ListCreateAPIView):
    """List all harvest records or create a new harvest record"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HarvestRecordCreateSerializer
        return HarvestRecordSerializer
    
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
    """Get, update or delete a specific harvest record"""
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HarvestRecord.objects.filter(user=self.request.user)


# ==================== LABOR VIEWS ====================

class LaborListCreateView(generics.ListCreateAPIView):
    """List all labor records or create a new labor record"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LaborCreateSerializer
        return LaborSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Labour.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        crop_id = self.request.data.get('crop')
        if isinstance(crop_id, str):
            crop_id = uuid.UUID(crop_id)
        crop = get_object_or_404(Crop, id=crop_id, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)


class LaborDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific labor record"""
    serializer_class = LaborSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Labour.objects.filter(user=self.request.user)


# ==================== NESTED VIEWS (UNDER SPECIFIC CROP) ====================

class CropFertilizersView(generics.ListCreateAPIView):
    """List all fertilizers for a specific crop or create new fertilizer"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FertilizerRecordCreateSerializer
        return FertilizerRecordSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
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
    """List all pesticides for a specific crop or create new pesticide"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PesticideRecordCreateSerializer
        return PesticideRecordSerializer
    
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
    """List all expenses for a specific crop or create new expense"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CropExpenseCreateSerializer
        return CropExpenseSerializer
    
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
    """List all incomes for a specific crop or create new income"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CropIncomeCreateSerializer
        return CropIncomeSerializer
    
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
    """List all harvests for a specific crop or create new harvest"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HarvestRecordCreateSerializer
        return HarvestRecordSerializer
    
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


class CropLaborView(generics.ListCreateAPIView):
    """List all labor records for a specific crop or create new labor record"""
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LaborCreateSerializer
        return LaborSerializer
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        return Labour.objects.filter(crop=crop, user=self.request.user)
    
    def perform_create(self, serializer):
        crop_pk = self.kwargs['crop_pk']
        if isinstance(crop_pk, str):
            crop_pk = uuid.UUID(crop_pk)
        crop = get_object_or_404(Crop, id=crop_pk, farmer=self.request.user)
        serializer.save(user=self.request.user, crop=crop)
        

class CropRecommendationView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CropRecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        farmer_data = serializer.validated_data

        crops_qs = CropKnowledgeBase.objects.all()

        # Run recommendation engine
        result = get_recommendations(crops_qs, farmer_data)

        if not result.get('success'):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        history_data = {
            'farmer': request.user,
            'soil_type': farmer_data.get('soil_type', 'loamy'),
            'ph': farmer_data.get('ph'),
            'season': farmer_data.get('season'),
            'water_availability': farmer_data.get('water_source', 'rainfed_only'),
            'region': farmer_data.get('region', 'terai'),
            'temperature': farmer_data.get('temperature_override'),
            'frost_risk': farmer_data.get('elevation_risk'),
            'experience': farmer_data.get('labor_availability', 'medium'),  
            'goal': farmer_data.get('farming_goal', 'mixed'),
            'recommendations': result.get('recommendations', [])
        }
        CropRecommendationHistory.objects.create(**history_data)

        return Response(result, status=status.HTTP_200_OK)


class CropRecommendationHistoryView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = CropRecommendationHistory.objects.filter(farmer=request.user).order_by('-created_at')[:20]
        serializer = CropRecommendationHistorySerializer(history, many=True)
        return Response({
            'success': True,
            'count': len(history),
            'history': serializer.data
        })

    def delete(self, request, history_id=None):
        if not history_id:
            return Response({
                'success': False,
                'error': 'History ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            history = CropRecommendationHistory.objects.get(id=history_id, farmer=request.user)
            history.delete()
            return Response({
                'success': True,
                'message': 'History entry deleted'
            })
        except CropRecommendationHistory.DoesNotExist:
            return Response({
                'success': False,
                'error': 'History entry not found'
            }, status=status.HTTP_404_NOT_FOUND)