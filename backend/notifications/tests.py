from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from notifications.models import Notification
from notifications.utils import generate_user_alerts_and_reminders_if_needed
from crops.models import Crop, CropTypeConfig, CropActivityRule
from livestock.models import Animal, VaccinationRecord

User = get_user_model()


class NotificationGenerationTriggerTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testfarmer3',
            email='farmer3@test.com',
            password='testpassword123',
            geographical_region='terai',
            is_farmer=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Setup configs and rules to trigger reminders
        self.paddy_config = CropTypeConfig.objects.create(
            crop_name='Paddy',
            region='terai',
            season='summer',
            vegetative_start_day=11,
            vegetative_end_day=40,
            total_growing_days=120,
            is_active=True
        )
        
        self.fertilizer_rule = CropActivityRule.objects.create(
            crop_config=self.paddy_config,
            growth_stage='vegetative',
            title='Apply Basal Fertilizer',
            description='Apply basal fertilizer',
            day_offset=10,
        )

    def test_alert_generation_triggered_once_per_day(self):
        """Test that alert generation runs on first access, but is not run again on second access"""
        today = date.today()
        
        # Create a crop that should trigger an advance reminder (planted 14 days ago)
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=14)
        )
        
        self.assertIsNone(self.user.last_reminder_generation)
        self.assertEqual(Notification.objects.filter(farmer=self.user).count(), 0)
        
        # Accessing notification list API endpoint should automatically generate reminders/alerts
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User generation date should now be set to today
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_reminder_generation, today)
        
        # Verify a crop notification was created
        notif_count = Notification.objects.filter(farmer=self.user).count()
        self.assertEqual(notif_count, 1)
        
        # If we delete the generated notification and hit list API again on the same day, it should NOT regenerate
        Notification.objects.all().delete()
        response2 = self.client.get('/api/notifications/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        self.assertEqual(Notification.objects.filter(farmer=self.user).count(), 0)
