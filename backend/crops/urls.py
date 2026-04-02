from django.urls import path
from . import views

urlpatterns = [
    # Main Crop URLs
    path('', views.CropListCreateView.as_view(), name='crop-list'),
    path('<uuid:pk>/', views.CropDetailView.as_view(), name='crop-detail'),
    
    # Fertilizer URLs
    path('fertilizers/', views.FertilizerListCreateView.as_view(), name='fertilizer-list'),
    path('fertilizers/<uuid:pk>/', views.FertilizerDetailView.as_view(), name='fertilizer-detail'),
    
    # Pesticide URLs
    path('pesticides/', views.PesticideListCreateView.as_view(), name='pesticide-list'),
    path('pesticides/<uuid:pk>/', views.PesticideDetailView.as_view(), name='pesticide-detail'),
    
    # NEW: Crop Expense URLs
    path('expenses/', views.CropExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/<uuid:pk>/', views.CropExpenseDetailView.as_view(), name='expense-detail'),
    
    # NEW: Crop Income URLs
    path('incomes/', views.CropIncomeListCreateView.as_view(), name='income-list'),
    path('incomes/<uuid:pk>/', views.CropIncomeDetailView.as_view(), name='income-detail'),
    
    # NEW: Harvest Record URLs
    path('harvests/', views.HarvestRecordListCreateView.as_view(), name='harvest-list'),
    path('harvests/<uuid:pk>/', views.HarvestRecordDetailView.as_view(), name='harvest-detail'),
    
    # Nested URLs (under specific crop)
    path('<int:crop_pk>/fertilizers/', views.CropFertilizersView.as_view(), name='crop-fertilizers'),
    path('<int:crop_pk>/pesticides/', views.CropPesticidesView.as_view(), name='crop-pesticides'),
    
    # Nested URLs
    path('<uuid:crop_pk>/fertilizers/', views.CropFertilizersView.as_view(), name='crop-fertilizers'),
    path('<uuid:crop_pk>/pesticides/', views.CropPesticidesView.as_view(), name='crop-pesticides'),
    path('<uuid:crop_pk>/expenses/', views.CropExpensesView.as_view(), name='crop-expenses'),
    path('<uuid:crop_pk>/incomes/', views.CropIncomesView.as_view(), name='crop-incomes'),
    path('<uuid:crop_pk>/harvests/', views.CropHarvestsView.as_view(), name='crop-harvests'),
]