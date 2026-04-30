from rest_framework import serializers

class CurrentWeatherSerializer(serializers.Serializer):
    """Serializer for current weather"""
    temperature = serializers.FloatField()
    feels_like = serializers.FloatField()
    humidity = serializers.IntegerField()
    pressure = serializers.IntegerField()
    wind_speed = serializers.FloatField()
    wind_degree = serializers.IntegerField()
    clouds = serializers.IntegerField()
    uvi = serializers.FloatField()
    visibility = serializers.IntegerField()
    condition = serializers.CharField()
    icon = serializers.CharField()
    rain = serializers.FloatField()
    snow = serializers.FloatField()
    sunrise = serializers.CharField()
    sunset = serializers.CharField()

class HourlyForecastSerializer(serializers.Serializer):
    """Serializer for hourly forecast"""
    time = serializers.CharField()
    hour = serializers.CharField()
    temperature = serializers.FloatField()
    feels_like = serializers.FloatField()
    humidity = serializers.IntegerField()
    condition = serializers.CharField()
    icon = serializers.CharField()
    rain_chance = serializers.IntegerField()
    rain = serializers.FloatField()
    wind_speed = serializers.FloatField()

class DailyForecastSerializer(serializers.Serializer):
    """Serializer for daily forecast"""
    date = serializers.CharField()
    day = serializers.CharField()
    min_temp = serializers.FloatField()
    max_temp = serializers.FloatField()
    morning_temp = serializers.FloatField()
    evening_temp = serializers.FloatField()
    night_temp = serializers.FloatField()
    humidity = serializers.IntegerField()
    condition = serializers.CharField()
    icon = serializers.CharField()
    rain_chance = serializers.IntegerField()
    rain = serializers.FloatField()
    snow = serializers.FloatField()
    uvi = serializers.FloatField()
    wind_speed = serializers.FloatField()
    sunrise = serializers.CharField()
    sunset = serializers.CharField()

class AlertSerializer(serializers.Serializer):
    """Serializer for weather alerts"""
    sender = serializers.CharField()
    event = serializers.CharField()
    description = serializers.CharField()
    start = serializers.CharField()
    end = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())

class CompleteWeatherSerializer(serializers.Serializer):
    """Serializer for complete weather data"""
    success = serializers.BooleanField()
    city = serializers.CharField()
    country = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    timezone = serializers.CharField()
    current = CurrentWeatherSerializer()
    hourly_forecast = HourlyForecastSerializer(many=True)
    daily_forecast = DailyForecastSerializer(many=True)
    alerts = AlertSerializer(many=True)

class AdviceSerializer(serializers.Serializer):
    """Serializer for farming advice"""
    type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    action = serializers.CharField()