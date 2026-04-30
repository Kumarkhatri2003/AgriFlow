from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import WeatherService

class WeatherView(APIView):
    """
    Get current weather + daily forecast
    URL: /api/weather/?city=Kathmandu
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        city = request.query_params.get('city', 'Kathmandu')
        
        weather_data = WeatherService.get_weather(city)
        
        if weather_data.get('success'):
            return Response({
                'success': True,
                'data': weather_data
            })
        else:
            return Response({
                'success': False,
                'error': weather_data.get('error', 'Unknown error')
            }, status=status.HTTP_400_BAD_REQUEST)


class FarmingAdviceView(APIView):
    """
    Get farming advice based on weather
    URL: /api/weather/advice/?city=Kathmandu
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        city = request.query_params.get('city', 'Kathmandu')
        
        weather_data = WeatherService.get_weather(city)
        
        if not weather_data.get('success'):
            return Response({
                'success': False,
                'error': weather_data.get('error', 'Cannot get weather data')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        advice = WeatherService.get_farming_advice(weather_data)
        
        return Response({
            'success': True,
            'city': weather_data.get('city'),
            'country': weather_data.get('country'),
            'current_weather': weather_data.get('current'),
            'daily_forecast': weather_data.get('daily_forecast'),
            'advice': advice
        })