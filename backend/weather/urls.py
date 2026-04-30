from django.urls import path
from . import views

urlpatterns = [
    path('', views.WeatherView.as_view(), name='weather'),
    
    path('advice/', views.FarmingAdviceView.as_view(), name='farming-advice'),
]