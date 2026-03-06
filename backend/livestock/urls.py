from django.urls import path
from . import views


urlpatterns = [
    path('animal-types/',views.AnimalTypeListView.as_view(),name='animal-type-list'),
    path('animal-types/<int:pk>/',views.AnimalTypeDetailView.as_view(),name='animal-type-detail'),
    
    
    path('animal/',views.AnimalListCreateView.as_view(),name='animal-list'),
    path('animal/<uuid:pk>/',views.AnimalDetailView.as_view(),name='animal-detail'),
    
    
    path('animals/type/<int:type_id>/', views.AnimalByTypeView.as_view(), name="animals-by-type"),
    path('animals/pregnant/', views.PregnantAnimalView.as_view(),name='pregnant-animals')
]
