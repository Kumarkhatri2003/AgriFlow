from django.urls import path
from . import views

urlpatterns = [
    # Crop URLs
    path('', views.CropListCreateView.as_view(), name='crop-list'),
    path('<int:pk>/', views.CropDetailView.as_view(), name='crop-detail'),
    
    # Fertilizer URLs
    path('fertilizers/', views.FertilizerListCreateView.as_view(), name='fertilizer-list'),
    path('fertilizers/<uuid:pk>/', views.FertilizerDetailView.as_view(), name='fertilizer-detail'),
    
    # Pesticide URLs
    path('pesticides/', views.PesticideListCreateView.as_view(), name='pesticide-list'),
    path('pesticides/<uuid:pk>/', views.PesticideDetailView.as_view(), name='pesticide-detail'),
    
    # Nested URLs (fertilizers/pesticides under a specific crop)
    path('<int:crop_pk>/fertilizers/', views.CropFertilizersView.as_view(), name='crop-fertilizers'),
    path('<int:crop_pk>/pesticides/', views.CropPesticidesView.as_view(), name='crop-pesticides'),
]