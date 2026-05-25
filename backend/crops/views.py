from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from datetime import date

from admin_panel.models import Notification
from .services.reminder_service import CropReminderService
from .expert_system import get_recommendations
from .models import (
    Crop, CropRecommendationHistory, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord, Labour, CropKnowledgeBase, 
    CropTypeConfig, CropActivityRule
)

from .serializers import (
    CropKnowledgeBaseSerializer,
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
    CropTypeConfigSerializer, 
    CropActivityRuleSerializer
)
import uuid

# ==================== MAIN CROP VIEWS ====================

class CropListCreateView(generics.ListCreateAPIView):
    """List all crops or create a new crop"""
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Crop.objects.filter(farmer=self.request.user)
        # Auto-update growth stages for active crops
        for crop in queryset.filter(status='active'):
            crop.update_growth_stage(save=True)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)


class CropDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific crop"""
    serializer_class = CropSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Crop.objects.filter(farmer=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'active':
            instance.update_growth_stage(save=True)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


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


# ====================CROP RECOMMENDATION VIEWS ====================

class CropRecommendationView(APIView):
    """
    POST /api/crops/recommend/
    Get crop recommendations based on farm conditions
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CropRecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        farmer_data = serializer.validated_data

        # Get all crops from knowledge base
        crops_qs = CropKnowledgeBase.objects.all()

        # Run recommendation engine
        result = get_recommendations(crops_qs, farmer_data)

        if not result.get('success'):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        # Prepare history data with ALL fields
        history_data = {
            'farmer': request.user,
            # Required fields
            'region': farmer_data.get('region', 'terai'),
            'season': farmer_data.get('season'),
            'water_source': farmer_data.get('water_source', 'rainfed_only'),
            'soil_type': farmer_data.get('soil_type', 'loamy'),
            'labor_availability': farmer_data.get('labor_availability', 'medium'),
            'market_distance': farmer_data.get('market_distance', 'near'),
            'farming_goal': farmer_data.get('farming_goal', 'mixed'),
            # New required fields
            'temperature': farmer_data.get('temperature'),
            'frost_risk': farmer_data.get('frost_risk') == 'yes',
            'drought_risk': farmer_data.get('drought_risk', 'medium'),
            # Optional fields
            'ph': farmer_data.get('ph'),
            'n': farmer_data.get('n'),
            'p': farmer_data.get('p'),
            'k': farmer_data.get('k'),
            # Results
            'recommendations': result.get('recommendations', [])
        }
        
        # Create history entry
        CropRecommendationHistory.objects.create(**history_data)

        # Add warning messages to response if any
        response_data = result
        if hasattr(serializer, '_npk_warning'):
            response_data['npk_warning'] = serializer._npk_warning
        if hasattr(serializer, '_frost_warning'):
            response_data['frost_warning'] = serializer._frost_warning
        if hasattr(serializer, '_temp_warning'):
            response_data['temp_warning'] = serializer._temp_warning

        return Response(response_data, status=status.HTTP_200_OK)


class CropRecommendationHistoryView(APIView):
    """
    GET /api/crops/recommend/history/
    Get user's recommendation history
    
    DELETE /api/crops/recommend/history/{id}/
    Delete a specific history entry
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        history = CropRecommendationHistory.objects.filter(
            farmer=request.user
        ).order_by('-created_at')[:20]
        
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
            history = CropRecommendationHistory.objects.get(
                id=history_id, 
                farmer=request.user
            )
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


# ==================== CROP TYPE CONFIG VIEWS ====================

from admin_panel.permissions import IsAdminUser as PanelAdminUser

class CropTypeConfigListView(generics.ListCreateAPIView):
    """
    GET /api/crop-configs/ - List all crop type configurations
    POST /api/crop-configs/ - Create new config (Admin only)
    """
    queryset = CropTypeConfig.objects.all()
    serializer_class = CropTypeConfigSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), PanelAdminUser()]
    
    def get_queryset(self):
        # Allow admins to see inactive configs, normal users only active
        is_admin = getattr(self.request.user, 'is_admin', False)
        if is_admin:
            queryset = CropTypeConfig.objects.all()
        else:
            queryset = CropTypeConfig.objects.filter(is_active=True)
        
        # Filter by crop_name
        crop_name = self.request.query_params.get('crop_name')
        if crop_name:
            queryset = queryset.filter(crop_name__iexact=crop_name)
        
        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        return queryset


class CropTypeConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/crop-configs/{id}/
    PUT /api/crop-configs/{id}/
    DELETE /api/crop-configs/{id}/
    """
    queryset = CropTypeConfig.objects.all()
    serializer_class = CropTypeConfigSerializer
    permission_classes = [IsAuthenticated, PanelAdminUser]
    lookup_field = 'id'


# ==================== CROP ACTIVITY RULE VIEWS ====================

class CropActivityRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CropActivityRule with CRUD operations
    GET /api/crop-activity-rules/
    POST /api/crop-activity-rules/
    GET /api/crop-activity-rules/{id}/
    PUT /api/crop-activity-rules/{id}/
    PATCH /api/crop-activity-rules/{id}/
    DELETE /api/crop-activity-rules/{id}/
    """
    queryset = CropActivityRule.objects.all()
    serializer_class = CropActivityRuleSerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), PanelAdminUser()]
    
    def get_queryset(self):
        # Allow admins to see inactive rules, normal users only active
        is_admin = getattr(self.request.user, 'is_admin', False)
        if is_admin:
            queryset = CropActivityRule.objects.all()
        else:
            queryset = CropActivityRule.objects.filter(is_active=True)
        
        # Filter by crop_config
        crop_config_id = self.request.query_params.get('crop_config')
        if crop_config_id:
            queryset = queryset.filter(crop_config_id=crop_config_id)
        
        # Filter by growth_stage
        growth_stage = self.request.query_params.get('growth_stage')
        if growth_stage:
            queryset = queryset.filter(growth_stage=growth_stage)
        
        # Filter by is_active
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def perform_destroy(self, instance):
        """Soft delete - just mark as inactive"""
        instance.is_active = False
        instance.save()


# ==================== CROP KNOWLEDGE BASE VIEWS ====================

class CropKnowledgeBaseListView(generics.ListCreateAPIView):
    """
    GET /api/crops/knowledge-base/ - List knowledge base entries
    POST /api/crops/knowledge-base/ - Create a knowledge base entry (Admin only)
    """
    queryset = CropKnowledgeBase.objects.all()
    serializer_class = CropKnowledgeBaseSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), PanelAdminUser()]

    def get_queryset(self):
        queryset = CropKnowledgeBase.objects.all()
        from django.db.models import Q
        
        # Search by english or nepali name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name_en__icontains=search) | 
                Q(name_np__icontains=search)
            )
            
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        season = self.request.query_params.get('season')
        if season:
            queryset = queryset.filter(best_season=season)
            
        drought_tolerance = self.request.query_params.get('drought_tolerance')
        if drought_tolerance:
            queryset = queryset.filter(drought_tolerance=drought_tolerance)
        
        frost_sensitive = self.request.query_params.get('frost_sensitive')
        if frost_sensitive:
            queryset = queryset.filter(frost_sensitive=frost_sensitive)
        
        return queryset


class CropKnowledgeBaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/crops/knowledge-base/{id}/ - Get details of a knowledge base entry
    PUT /api/crops/knowledge-base/{id}/ - Update a knowledge base entry (Admin only)
    DELETE /api/crops/knowledge-base/{id}/ - Delete a knowledge base entry (Admin only)
    """
    queryset = CropKnowledgeBase.objects.all()
    serializer_class = CropKnowledgeBaseSerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), PanelAdminUser()]


# ==================== CROP CONFIGURATION OPTIONS VIEWS ====================

class CropConfigOptionsView(generics.GenericAPIView):
    """
    GET /api/crop-config-options/
    Get all crop configs grouped for dropdown with "Other" option support
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        configs = CropTypeConfig.objects.filter(is_active=True).select_related()
        
        # Group by crop_name
        grouped = {}
        for config in configs:
            crop_name = config.crop_name
            if crop_name not in grouped:
                grouped[crop_name] = []
            
            grouped[crop_name].append({
                'id': config.id,
                'display_name': config.get_display_name(),
                'variety': config.variety or '',
                'region': config.region or '',
                'season': config.season or '',
            })
        
        # Get list of crop names
        crop_names = list(grouped.keys())
        
        return Response({
            'configured_crops': crop_names,
            'crop_configs': grouped,
            'has_configured_crops': len(crop_names) > 0
        })


class AvailableCropsView(generics.GenericAPIView):
    """
    GET /api/available-crops/
    Get list of available crops with their varieties, regions, seasons
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get unique crop names with their config count
        crops = CropTypeConfig.objects.filter(is_active=True).values('crop_name').distinct().order_by('crop_name')
        
        result = []
        for crop in crops:
            crop_name = crop['crop_name']
            
            # Get all configs for this crop
            configs = CropTypeConfig.objects.filter(crop_name=crop_name, is_active=True)
            
            # Extract unique values
            varieties = list(configs.exclude(variety='').values_list('variety', flat=True).distinct())
            regions = list(configs.values_list('region', flat=True).distinct())
            seasons = list(configs.exclude(season__isnull=True).values_list('season', flat=True).distinct())
            
            # Get region display names
            region_display_map = dict(CropTypeConfig.REGION_CHOICES)
            region_displays = [region_display_map.get(r, r) for r in regions]
            
            # Get season display names
            season_display_map = dict(CropTypeConfig.SEASON_CHOICES)
            season_displays = [season_display_map.get(s, s) for s in seasons]
            
            result.append({
                'crop_name': crop_name,
                'varieties': varieties,
                'regions': regions,
                'region_displays': region_displays,
                'seasons': seasons,
                'season_displays': season_displays,
                'has_config': True
            })
        
        return Response({
            'crops': result,
            'total': len(result)
        })


# ==================== REMINDER VIEWS ====================

class GenerateCropRemindersView(generics.GenericAPIView):
    """
    POST /api/crops/reminders/generate/
    Manually generate reminders for user's crops
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        crops = Crop.objects.filter(farmer=request.user, status='active')
        total_reminders = 0
        results = []
        
        for crop in crops:
            reminders = CropReminderService.generate_reminders_for_crop(crop)
            total_reminders += len(reminders)
            results.append({
                'crop_id': str(crop.id),
                'crop_name': crop.name,
                'reminders': len(reminders)
            })
        
        return Response({
            'success': True,
            'total_crops': crops.count(),
            'total_reminders': total_reminders,
            'results': results
        })


class PendingCropActivitiesView(generics.GenericAPIView):
    """
    GET /api/crops/reminders/pending/
    Get pending crop activities from notifications
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from notifications.models import Notification
        from notifications.i18n import get_request_language, notification_to_dict

        lang = get_request_language(request)
        pending = Notification.objects.filter(
            farmer=request.user,
            notification_type='crop',
            is_completed=False,
        ).order_by('-priority', '-created_at')

        return Response({
            'success': True,
            'lang': lang,
            'total': pending.count(),
            'activities': [notification_to_dict(n, lang) for n in pending],
        })


class CropRemindersByCropView(generics.GenericAPIView):
    """
    POST /api/crops/{crop_id}/reminders/generate/
    Generate reminders for a specific crop
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, crop_id):
        try:
            crop = Crop.objects.get(id=crop_id, farmer=request.user, status='active')
            reminders = CropReminderService.generate_reminders_for_crop(crop)
            
            return Response({
                'success': True,
                'crop_id': str(crop.id),
                'crop_name': crop.name,
                'reminders_generated': len(reminders),
                'reminders': [
                    {
                        'id': r.id,
                        'title': r.title,
                        'priority': r.priority,
                        'created_at': r.created_at.isoformat()
                    }
                    for r in reminders
                ]
            })
        except Crop.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Crop not found'
            }, status=status.HTTP_404_NOT_FOUND)


class MarkCropActivityReadView(generics.GenericAPIView):
    """
    POST /api/crops/reminders/{notification_id}/read/
    Mark a crop activity notification as read
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, notification_id):
        from notifications.models import Notification
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                farmer=request.user,
                notification_type='crop'
            )
            notification.mark_as_read()
            
            return Response({
                'success': True,
                'message': 'Activity marked as read'
            })
        except Notification.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Notification not found'
            }, status=status.HTTP_404_NOT_FOUND)


# ==================== STATISTICS VIEW ====================

class CropReminderStatsView(generics.GenericAPIView):
    """
    GET /api/crops/reminders/stats/
    Get reminder statistics for the farmer
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get crop counts
        total_crops = Crop.objects.filter(farmer=request.user).count()
        active_crops = Crop.objects.filter(farmer=request.user, status='active').count()
        
        # Get notification stats
        today = date.today()
        
        pending_today = Notification.objects.filter(
            farmer=request.user,
            notification_type='crop',
            is_read=False,
            created_at__date=today
        ).count()
        
        pending_total = Notification.objects.filter(
            farmer=request.user,
            notification_type='crop',
            is_read=False
        ).count()
        
        # Get by priority
        critical_count = Notification.objects.filter(
            farmer=request.user,
            notification_type='crop',
            is_read=False,
            priority='critical'
        ).count()
        
        warning_count = Notification.objects.filter(
            farmer=request.user,
            notification_type='crop',
            is_read=False,
            priority='medium'
        ).count()
        
        return Response({
            'success': True,
            'crops': {
                'total': total_crops,
                'active': active_crops
            },
            'notifications': {
                'pending_today': pending_today,
                'pending_total': pending_total,
                'critical': critical_count,
                'warning': warning_count
            }
        })