from django.urls import path
from . import views

urlpatterns = [
    # Animal Type URLs
    path('animal-types/', views.AnimalTypeListView.as_view(), name='animal-type-list'),
    path('animal-types/<int:pk>/', views.AnimalTypeDetailView.as_view(), name='animal-type-detail'),
    
    # Animal URLs
    path('animals/', views.AnimalListCreateView.as_view(), name='animal-list'),
    path('animals/<uuid:pk>/', views.AnimalDetailView.as_view(), name='animal-detail'),
    
    # Filtered Animal Views
    path('animals/type/<int:type_id>/', views.AnimalByTypeView.as_view(), name='animals-by-type'),
    path('animals/pregnant/', views.PregnantAnimalView.as_view(), name='pregnant-animals'),
    path('animals/active/', views.ActiveAnimalsView.as_view(), name='active-animals'),
    
    # Vaccination URLs
    path('vaccinations/', views.VaccinationRecordListCreateView.as_view(), name='vaccination-list'),
    path('vaccinations/<uuid:pk>/', views.VaccinationRecordDetailView.as_view(), name='vaccination-detail'),
    
    # Health Record URLs
    path('health-records/', views.HealthRecordListCreateView.as_view(), name='health-list'),
    path('health-records/<uuid:pk>/', views.HealthRecordDetailView.as_view(), name='health-detail'),
    
    # Milk Record URLs
    path('milk-records/', views.MilkRecordListCreateView.as_view(), name='milk-list'),
    path('milk-records/<uuid:pk>/', views.MilkRecordDetailView.as_view(), name='milk-detail'),
    
    # Breeding Record URLs
    path('breeding-records/', views.BreedingRecordListCreateView.as_view(), name='breeding-list'),
    path('breeding-records/<uuid:pk>/', views.BreedingRecordDetailView.as_view(), name='breeding-detail'),
    
    # Animal Income URLs
    path('incomes/', views.AnimalIncomeListCreateView.as_view(), name='income-list'),
    path('incomes/<uuid:pk>/', views.AnimalIncomeDetailView.as_view(), name='income-detail'),
    
    # Animal Expense URLs
    path('expenses/', views.AnimalExpenseListCreateView.as_view(), name='expense-list'),
    path('expenses/<uuid:pk>/', views.AnimalExpenseDetailView.as_view(), name='expense-detail'),
    
    # Nested URLs (under specific animal)
    path('animals/<uuid:animal_pk>/vaccinations/', views.AnimalVaccinationsView.as_view(), name='animal-vaccinations'),
    path('animals/<uuid:animal_pk>/health-records/', views.AnimalHealthRecordsView.as_view(), name='animal-health'),
    path('animals/<uuid:animal_pk>/milk-records/', views.AnimalMilkRecordsView.as_view(), name='animal-milk'),
    path('animals/<uuid:animal_pk>/breeding-records/', views.AnimalBreedingRecordsView.as_view(), name='animal-breeding'),
    path('animals/<uuid:animal_pk>/incomes/', views.AnimalIncomesView.as_view(), name='animal-incomes'),
    path('animals/<uuid:animal_pk>/expenses/', views.AnimalExpensesView.as_view(), name='animal-expenses'),
]