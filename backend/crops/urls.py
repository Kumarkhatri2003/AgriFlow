# crops/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ==================== CROP OPTIONS ENDPOINTS (MUST BE BEFORE catch-all) ====================
    path('available-crops/', views.AvailableCropsView.as_view(), name='available-crops'),
    path('crop-varieties/', views.CropVarietiesView.as_view(), name='crop-varieties'),
    path('crop-config-options/', views.CropConfigOptionsView.as_view(), name='crop-config-options'),
    
    # ==================== MAIN CROP URLs ====================
    path('', views.CropListCreateView.as_view(), name='crop-list'),
    path('<uuid:pk>/', views.CropDetailView.as_view(), name='crop-detail'),
    
    # ==================== REMINDER ENDPOINTS ====================
    path('reminders/generate/', views.GenerateCropRemindersView.as_view(), name='generate-reminders'),
    path('reminders/pending/', views.PendingCropActivitiesView.as_view(), name='pending-activities'),
    path('reminders/stats/', views.CropReminderStatsView.as_view(), name='reminder-stats'),
    path('reminders/<int:notification_id>/read/', views.MarkCropActivityReadView.as_view(), name='mark-activity-read'),
    path('<uuid:crop_id>/reminders/generate/', views.CropRemindersByCropView.as_view(), name='crop-reminders'),
    
    # ==================== RECOMMENDATION ENDPOINTS ====================
    path('recommend/', views.CropRecommendationView.as_view(), name='crop-recommend'),
    path('recommend/history/', views.CropRecommendationHistoryView.as_view(), name='recommend-history'),
    path('recommend/history/<int:history_id>/', views.CropRecommendationHistoryView.as_view(), name='recommend-history-detail'),
    
    # ==================== FERTILIZER URLs ====================
    path('fertilizers/', views.FertilizerListCreateView.as_view(), name='fertilizer-list'),
    path('fertilizers/<uuid:pk>/', views.FertilizerDetailView.as_view(), name='fertilizer-detail'),
    
    # ==================== PESTICIDE URLs ====================
    path('pesticides/', views.PesticideListCreateView.as_view(), name='pesticide-list'),
    path('pesticides/<uuid:pk>/', views.PesticideDetailView.as_view(), name='pesticide-detail'),
    
    # ==================== CROP EXPENSE URLs ====================
    path('expenses/', views.CropExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/<uuid:pk>/', views.CropExpenseDetailView.as_view(), name='expense-detail'),
    
    # ==================== CROP INCOME URLs ====================
    path('incomes/', views.CropIncomeListCreateView.as_view(), name='income-list'),
    path('incomes/<uuid:pk>/', views.CropIncomeDetailView.as_view(), name='income-detail'),
    
    # ==================== HARVEST RECORD URLs ====================
    path('harvests/', views.HarvestRecordListCreateView.as_view(), name='harvest-list'),
    path('harvests/<uuid:pk>/', views.HarvestRecordDetailView.as_view(), name='harvest-detail'),
    
    # ==================== LABOR URLs ====================
    path('labor/', views.LaborListCreateView.as_view(), name='labor-list'),
    path('labor/<uuid:pk>/', views.LaborDetailView.as_view(), name='labor-detail'),
    
    # ==================== NESTED URLs (under specific crop) ====================
    path('<uuid:crop_pk>/fertilizers/', views.CropFertilizersView.as_view(), name='crop-fertilizers'),
    path('<uuid:crop_pk>/pesticides/', views.CropPesticidesView.as_view(), name='crop-pesticides'),
    path('<uuid:crop_pk>/expenses/', views.CropExpensesView.as_view(), name='crop-expenses'),
    path('<uuid:crop_pk>/incomes/', views.CropIncomesView.as_view(), name='crop-incomes'),
    path('<uuid:crop_pk>/harvests/', views.CropHarvestsView.as_view(), name='crop-harvests'),
    path('<uuid:crop_pk>/labor/', views.CropLaborView.as_view(), name='crop-labor'),
    
    # ==================== ADMIN CONFIG URLs ====================
    path('crop-configs/', views.CropTypeConfigListView.as_view(), name='crop-config-list'),
    path('crop-configs/<int:id>/', views.CropTypeConfigDetailView.as_view(), name='crop-config-detail'),
    path('knowledge-base/', views.CropKnowledgeBaseListView.as_view(), name='crop-knowledge-base-list'),
    path('knowledge-base/<int:pk>/', views.CropKnowledgeBaseDetailView.as_view(), name='crop-knowledge-base-detail'),
    path('crop-activity-rules/', views.CropActivityRuleViewSet.as_view({'get': 'list', 'post': 'create'}), name='crop-activity-rule-list'),
    path('crop-activity-rules/<int:id>/', views.CropActivityRuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='crop-activity-rule-detail'),
]