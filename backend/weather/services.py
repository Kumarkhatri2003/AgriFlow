import requests
from datetime import datetime
from django.conf import settings
from django.core.cache import cache

class WeatherService:
    """
    Service for WeatherAPI.com with caching
    Free tier: 1,000,000 calls/month
    """
    
    API_KEY = getattr(settings, 'WEATHER_API_KEY', None)
    BASE_URL = "http://api.weatherapi.com/v1"
    
    # Cache for 30 minutes (1800 seconds) - balances freshness and API savings
    CACHE_TIMEOUT = 1800  # 30 minutes
    
    @classmethod
    def _get_cache_key(cls, city_name):
        """Generate cache key for city"""
        return f"weather_{city_name.lower()}"
    
    @classmethod
    def get_weather(cls, city_name):
        """
        Get current weather + daily forecast with caching
        Cached for 30 minutes to save API calls
        """
        # Check cache first
        cache_key = cls._get_cache_key(city_name)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        
        if not cls.API_KEY:
            return {'success': False, 'error': 'WeatherAPI key not configured'}
        
        url = f"{cls.BASE_URL}/forecast.json"
        params = {
            'key': cls.API_KEY,
            'q': city_name,
            'days': 5,
            'aqi': 'no',
            'alerts': 'no'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Current weather
                current = {
                    'temperature': data['current']['temp_c'],
                    'feels_like': data['current']['feelslike_c'],
                    'humidity': data['current']['humidity'],
                    'pressure': data['current']['pressure_mb'],
                    'wind_speed': data['current']['wind_kph'],
                    'wind_degree': data['current']['wind_degree'],
                    'condition': data['current']['condition']['text'],
                    'icon': data['current']['condition']['icon'].split('/')[-1].split('.')[0],
                    'clouds': data['current']['cloud'],
                    'uv_index': data['current']['uv'],
                    'visibility': data['current']['vis_km'],
                    'sunrise': data['forecast']['forecastday'][0]['astro']['sunrise'],
                    'sunset': data['forecast']['forecastday'][0]['astro']['sunset'],
                }
                
                # Daily forecast (5 days)
                daily_forecast = []
                for day in data['forecast']['forecastday']:
                    daily_forecast.append({
                        'date': day['date'],
                        'day': datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A'),
                        'min_temp': day['day']['mintemp_c'],
                        'max_temp': day['day']['maxtemp_c'],
                        'avg_temp': day['day']['avgtemp_c'],
                        'condition': day['day']['condition']['text'],
                        'icon': day['day']['condition']['icon'].split('/')[-1].split('.')[0],
                        'rain_chance': day['day']['daily_chance_of_rain'],
                        'rain': day['day']['totalprecip_mm'],
                        'humidity': day['day']['avghumidity'],
                        'uv_index': day['day']['uv'],
                        'sunrise': day['astro']['sunrise'],
                        'sunset': day['astro']['sunset'],
                    })
                
                result = {
                    'success': True,
                    'city': data['location']['name'],
                    'country': data['location']['country'],
                    'latitude': data['location']['lat'],
                    'longitude': data['location']['lon'],
                    'timezone': data['location']['tz_id'],
                    'current': current,
                    'daily_forecast': daily_forecast,
                    'alerts': [],
                }
                
                # Save to cache for 30 minutes
                cache.set(cache_key, result, cls.CACHE_TIMEOUT)
                
                return result
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                return {'success': False, 'error': f"API error: {error_msg}"}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timed out. Please check your internet connection.'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Network error. Cannot connect to weather service.'}
        except Exception as e:
            return {'success': False, 'error': f'Error: {str(e)}'}
    
    @classmethod
    def get_farming_advice(cls, weather_data):
        """
        Generate farming advice based on weather conditions
        """
        if not weather_data.get('success'):
            return None
        
        advice_list = []
        current = weather_data.get('current', {})
        temp = current.get('temperature', 0)
        humidity = current.get('humidity', 0)
        condition = current.get('condition', '').lower()
        uv_index = current.get('uv_index', 0)
        
        # Get today's forecast for additional advice
        daily = weather_data.get('daily_forecast', [])
        today = daily[0] if daily else {}
        rain_today = today.get('rain_chance', 0)
        
        # Temperature advice
        if temp > 35:
            advice_list.append({
                'type': 'danger',
                'title': '🔥 Extreme Heat Warning!',
                'message': f'Very hot at {temp}°C! Your crops need extra care.',
                'action': 'Water early morning or evening. Use mulch to retain moisture.'
            })
        elif temp > 30:
            advice_list.append({
                'type': 'warning',
                'title': '⚠️ High Temperature Alert',
                'message': f'Temperature is {temp}°C. Monitor soil moisture.',
                'action': 'Increase irrigation frequency. Provide shade for sensitive plants.'
            })
        elif temp < 10:
            advice_list.append({
                'type': 'warning',
                'title': '❄️ Cold Weather Alert',
                'message': f'Cold at {temp}°C. Protect sensitive crops.',
                'action': 'Cover young plants. Delay planting new seeds.'
            })
        elif 20 <= temp <= 28:
            advice_list.append({
                'type': 'good',
                'title': '✅ Ideal Temperature',
                'message': f'Temperature is {temp}°C - perfect for crop growth.',
                'action': 'Continue normal farming activities. Good time for planting.'
            })
        
        # Rain advice
        if rain_today > 70:
            advice_list.append({
                'type': 'warning',
                'title': '🌧️ Heavy Rain Expected',
                'message': f'{rain_today}% chance of rain today.',
                'action': 'Avoid spraying pesticides. Check drainage systems.'
            })
        elif rain_today > 40:
            advice_list.append({
                'type': 'info',
                'title': '🌦️ Possible Rain',
                'message': f'{rain_today}% chance of rain.',
                'action': 'Keep harvesting equipment ready if needed.'
            })
        
        # Humidity advice
        if humidity > 85:
            advice_list.append({
                'type': 'warning',
                'title': '🦠 High Humidity Risk',
                'message': f'{humidity}% humidity - fungal diseases may develop.',
                'action': 'Inspect crops for fungus. Ensure good air circulation.'
            })
        elif humidity < 30:
            advice_list.append({
                'type': 'info',
                'title': '🏜️ Dry Air Conditions',
                'message': 'Low humidity increases evaporation from soil.',
                'action': 'Use mulch to retain soil moisture.'
            })
        
        # UV Index advice
        if uv_index > 8:
            advice_list.append({
                'type': 'warning',
                'title': '☀️ Extreme UV Index',
                'message': f'UV index is {uv_index} - very high!',
                'action': 'Work in shade during midday (10 AM - 4 PM). Wear protective clothing.'
            })
        elif uv_index > 5:
            advice_list.append({
                'type': 'info',
                'title': '🕶️ High UV Index',
                'message': f'UV index is {uv_index}.',
                'action': 'Wear hat and sunscreen when working outdoors.'
            })
        
        # Weather condition advice
        if 'rain' in condition:
            advice_list.append({
                'type': 'info',
                'title': '☔ Rainy Weather',
                'message': 'Rainy conditions make some tasks difficult.',
                'action': 'Do indoor farm maintenance. Avoid applying pesticides.'
            })
        elif 'clear' in condition or 'sun' in condition or 'sunny' in condition:
            advice_list.append({
                'type': 'good',
                'title': '☀️ Perfect Farming Weather',
                'message': 'Clear skies and good visibility.',
                'action': 'Great day for harvesting, planting, and spraying.'
            })
        
        if not advice_list:
            advice_list.append({
                'type': 'good',
                'title': '🌾 Normal Conditions',
                'message': 'Weather conditions are favorable for farming.',
                'action': 'Follow your regular farming schedule.'
            })
        
        return advice_list