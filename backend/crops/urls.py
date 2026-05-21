# crops/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main Crop URLs
    path('', views.CropListCreateView.as_view(), name='crop-list'),

    # Reminder endpoints (before <uuid:pk>/ catch-all detail routes)
    path('reminders/generate/', views.GenerateCropRemindersView.as_view(), name='generate-reminders'),
    path('reminders/pending/', views.PendingCropActivitiesView.as_view(), name='pending-activities'),
    path('reminders/stats/', views.CropReminderStatsView.as_view(), name='reminder-stats'),
    path('reminders/<int:notification_id>/read/', views.MarkCropActivityReadView.as_view(), name='mark-activity-read'),

    path('<uuid:pk>/', views.CropDetailView.as_view(), name='crop-detail'), 
    
    # Fertilizer URLs
    path('fertilizers/', views.FertilizerListCreateView.as_view(), name='fertilizer-list'),
    path('fertilizers/<uuid:pk>/', views.FertilizerDetailView.as_view(), name='fertilizer-detail'),
    
    # Pesticide URLs
    path('pesticides/', views.PesticideListCreateView.as_view(), name='pesticide-list'),
    path('pesticides/<uuid:pk>/', views.PesticideDetailView.as_view(), name='pesticide-detail'),
    
    # Crop Expense URLs
    path('expenses/', views.CropExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/<uuid:pk>/', views.CropExpenseDetailView.as_view(), name='expense-detail'),
    
    # Crop Income URLs
    path('incomes/', views.CropIncomeListCreateView.as_view(), name='income-list'),
    path('incomes/<uuid:pk>/', views.CropIncomeDetailView.as_view(), name='income-detail'),
    
    # Harvest Record URLs
    path('harvests/', views.HarvestRecordListCreateView.as_view(), name='harvest-list'),
    path('harvests/<uuid:pk>/', views.HarvestRecordDetailView.as_view(), name='harvest-detail'),
    
    # Labor URLs
    path('labor/', views.LaborListCreateView.as_view(), name='labor-list'),
    path('labor/<uuid:pk>/', views.LaborDetailView.as_view(), name='labor-detail'),
    
    # Nested URLs (under specific crop)
    path('<uuid:crop_pk>/fertilizers/', views.CropFertilizersView.as_view(), name='crop-fertilizers'),
    path('<uuid:crop_pk>/pesticides/', views.CropPesticidesView.as_view(), name='crop-pesticides'),
    path('<uuid:crop_pk>/expenses/', views.CropExpensesView.as_view(), name='crop-expenses'),
    path('<uuid:crop_pk>/incomes/', views.CropIncomesView.as_view(), name='crop-incomes'),
    path('<uuid:crop_pk>/harvests/', views.CropHarvestsView.as_view(), name='crop-harvests'),
    path('<uuid:crop_pk>/labor/', views.CropLaborView.as_view(), name='crop-labor'),
    
   path('recommend/', views.CropRecommendationView.as_view(), name='crop-recommend'),
    path('recommend/history/', views.CropRecommendationHistoryView.as_view(), name='recommend-history'),
    path('recommend/history/<int:history_id>/', views.CropRecommendationHistoryView.as_view(), name='recommend-history-detail'),
    
    path('api/crop-configs/', views.CropTypeConfigListView.as_view(), name='crop-config-list'),
    path('api/crop-configs/<int:id>/', views.CropTypeConfigDetailView.as_view(), name='crop-config-detail'),
    
    # Crop Knowledge Base URLs
    path('api/knowledge-base/', views.CropKnowledgeBaseListView.as_view(), name='crop-knowledge-base-list'),
    path('api/knowledge-base/<int:pk>/', views.CropKnowledgeBaseDetailView.as_view(), name='crop-knowledge-base-detail'),
    
    # Crop Activity Rule URLs
    path('api/crop-activity-rules/', views.CropActivityRuleViewSet.as_view({'get': 'list', 'post': 'create'}), name='crop-activity-rule-list'),
    path('api/crop-activity-rules/<int:id>/', views.CropActivityRuleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='crop-activity-rule-detail'),
    
    # Crop options endpoints
    path('api/crop-config-options/', views.CropConfigOptionsView.as_view(), name='crop-config-options'),
    path('api/available-crops/', views.AvailableCropsView.as_view(), name='available-crops'),

    path('<uuid:crop_id>/reminders/generate/', views.CropRemindersByCropView.as_view(), name='crop-reminders'),
]