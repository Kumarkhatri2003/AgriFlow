from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import Crop, CropTypeConfig, CropActivityRule

User = get_user_model()

class CropAutoGrowthStageTests(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testfarmer',
            email='farmer@test.com',
            password='testpassword123',
            geographical_region='terai'
        )
        
        # Authenticate the APIClient
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create a standard CropTypeConfig for Paddy (basmati variety, terai region)
        self.paddy_config = CropTypeConfig.objects.create(
            crop_name='Paddy',
            variety='Basmati',
            region='terai',
            season='summer',
            germination_start_day=0,
            germination_end_day=10,
            vegetative_start_day=11,
            vegetative_end_day=40,
            flowering_start_day=41,
            flowering_end_day=60,
            maturation_start_day=61,
            maturation_end_day=85,
            harvest_start_day=86,
            harvest_end_day=120,
            total_growing_days=120,
            is_active=True
        )

    def test_crop_creation_calculates_correct_growth_stage(self):
        """Test that creating a crop auto-calculates correct growth stage based on planting date"""
        today = date.today()
        
        # 1. Seeding stage (0 days since planting)
        crop_seeding = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today
        )
        self.assertEqual(crop_seeding.growth_stage, 'seeding')

        # 2. Vegetative stage (20 days since planting)
        crop_vegetative = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=20)
        )
        self.assertEqual(crop_vegetative.growth_stage, 'vegetative')

        # 3. Flowering stage (50 days since planting)
        crop_flowering = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=50)
        )
        self.assertEqual(crop_flowering.growth_stage, 'flowering')

        # 4. Fruiting stage (70 days since planting)
        crop_fruiting = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=70)
        )
        self.assertEqual(crop_fruiting.growth_stage, 'fruiting')

        # 5. Harvest stage (90 days since planting)
        crop_harvest = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=90)
        )
        self.assertEqual(crop_harvest.growth_stage, 'harvest')

    def test_updating_planting_date_updates_growth_stage(self):
        """Test that updating the planting date correctly recalculates and saves the growth stage"""
        today = date.today()
        
        # Start at seeding
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today
        )
        self.assertEqual(crop.growth_stage, 'seeding')
        
        # Change planting date to 20 days ago (vegetative) and save
        crop.planting_date = today - timedelta(days=20)
        crop.save()
        self.assertEqual(crop.growth_stage, 'vegetative')
        
        # Change to 50 days ago (flowering) and save
        crop.planting_date = today - timedelta(days=50)
        crop.save()
        self.assertEqual(crop.growth_stage, 'flowering')

    def test_fallback_when_no_config_found(self):
        """Test fallback behavior when no configuration is matched (should keep current growth_stage)"""
        today = date.today()
        
        # Create a crop with a non-existent name to ensure no CropTypeConfig match
        crop = Crop.objects.create(
            farmer=self.user,
            name='Exotic Crop',
            variety='Special-1',
            field_name='West Field',
            field_area=2.0,
            planting_date=today,
            growth_stage='vegetative'  # Pass explicit stage
        )
        # Should retain the passed growth_stage since there is no matching config
        self.assertEqual(crop.growth_stage, 'vegetative')

    def test_api_list_updates_growth_stage(self):
        """Test that fetching crops via GET list API triggers growth stage updates and returns it"""
        today = date.today()
        
        # Create a crop planted today (initially 'seeding')
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='East Field',
            field_area=1.0,
            planting_date=today
        )
        self.assertEqual(crop.growth_stage, 'seeding')
        
        # Directly update the database to simulate passage of time without saving through model
        Crop.objects.filter(id=crop.id).update(planting_date=today - timedelta(days=20))
        
        # Verify db field is currently stale and is still 'seeding' in database
        stale_crop = Crop.objects.get(id=crop.id)
        self.assertEqual(stale_crop.growth_stage, 'seeding')
        
        # Call GET list API
        response = self.client.get('/api/crops/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify API returned 'vegetative'
        self.assertEqual(response.data[0]['growth_stage'], 'vegetative')
        
        # Verify the database was updated
        db_crop = Crop.objects.get(id=crop.id)
        self.assertEqual(db_crop.growth_stage, 'vegetative')

    def test_api_detail_updates_growth_stage(self):
        """Test that retrieving a specific crop via GET detail API updates and returns the correct stage"""
        today = date.today()
        
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='West Field',
            field_area=1.0,
            planting_date=today
        )
        self.assertEqual(crop.growth_stage, 'seeding')
        
        # Simulate passage of time by modifying planting date in database directly
        Crop.objects.filter(id=crop.id).update(planting_date=today - timedelta(days=50))
        
        # Call GET detail API
        response = self.client.get(f'/api/crops/{crop.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify API returned 'flowering'
        self.assertEqual(response.data['growth_stage'], 'flowering')
        
        # Verify database was updated
        db_crop = Crop.objects.get(id=crop.id)
        self.assertEqual(db_crop.growth_stage, 'flowering')

    def test_planting_date_update_resets_manual_override_and_recalculates(self):
        """Test that updating the planting date resets manual override and recalculates stage"""
        today = date.today()
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='West Field',
            field_area=1.0,
            planting_date=today
        )
        self.assertEqual(crop.growth_stage, 'seeding')
        self.assertFalse(crop.growth_stage_manual_override)
        
        # Set manual stage to flowering
        crop.set_manual_growth_stage('flowering')
        self.assertEqual(crop.growth_stage, 'flowering')
        self.assertTrue(crop.growth_stage_manual_override)
        
        # Update planting date to 20 days ago (vegetative) and save
        crop.planting_date = today - timedelta(days=20)
        crop.save()
        
        # Verify override is reset and stage is recalculated
        self.assertFalse(crop.growth_stage_manual_override)
        self.assertEqual(crop.growth_stage, 'vegetative')

    def test_auto_harvest_when_system_date_exceeds_expected_harvest(self):
        """Test that a crop is marked as harvested if expected_harvest_date is in the past"""
        today = date.today()
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='West Field',
            field_area=1.0,
            planting_date=today - timedelta(days=30),
            expected_harvest_date=today - timedelta(days=1)
        )
        self.assertEqual(crop.status, 'harvested')
        self.assertEqual(crop.growth_stage, 'harvest')

    def test_auto_harvest_when_system_date_exceeds_calculated_harvest(self):
        """Test that a crop is marked as harvested if calculated harvest date is in the past"""
        today = date.today()
        # Paddy config total_growing_days=120. Planted 125 days ago.
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='West Field',
            field_area=1.0,
            planting_date=today - timedelta(days=125)
        )
        self.assertEqual(crop.status, 'harvested')
        self.assertEqual(crop.growth_stage, 'harvest')


class CropReminderAdvanceTests(TestCase):
    
    def setUp(self):
        # Disconnect signals to prevent auto-reminders during test crop creation
        from django.db.models.signals import post_save, pre_save
        from crops.signals import crop_created_or_updated, crop_status_change_handler
        post_save.disconnect(crop_created_or_updated, sender=Crop)
        pre_save.disconnect(crop_status_change_handler, sender=Crop)

        # Create a test user
        self.user = User.objects.create_user(
            username='testfarmer2',
            email='farmer2@test.com',
            password='testpassword123',
            geographical_region='terai'
        )
        
        # Create a standard CropTypeConfig for Paddy (basmati variety, terai region)
        self.paddy_config = CropTypeConfig.objects.create(
            crop_name='Paddy',
            variety='Basmati',
            region='terai',
            season='summer',
            germination_start_day=0,
            germination_end_day=10,
            vegetative_start_day=11,
            vegetative_end_day=40,
            flowering_start_day=41,
            flowering_end_day=60,
            maturation_start_day=61,
            maturation_end_day=85,
            harvest_start_day=86,
            harvest_end_day=120,
            total_growing_days=120,
            is_active=True
        )
        
        # Add a CropActivityRule for applying Basal Fertilizer on Day 10 of vegetative stage
        self.fertilizer_rule = CropActivityRule.objects.create(
            crop_config=self.paddy_config,
            growth_stage='vegetative',
            title='Apply Basal Fertilizer',
            description='Apply basal fertilizer for Paddy growth',
            measurements='Urea: 4.8 Kg/Ropani',
            day_offset=10,
            order=1
        )
    def tearDown(self):
        from django.db.models.signals import post_save, pre_save
        from crops.signals import crop_created_or_updated, crop_status_change_handler
        post_save.connect(crop_created_or_updated, sender=Crop)
        pre_save.connect(crop_status_change_handler, sender=Crop)

    def test_7_days_advance_reminder_generation(self):
        """Test that an advance reminder triggers exactly 7 days before scheduled day_offset"""
        from crops.services.reminder_service import CropReminderService
        from notifications.models import Notification
        
        today = date.today()
        # Scheduled day is day 10 of vegetative stage.
        # Vegetative stage starts at day 11. So scheduled absolute day is day 21 (11 + 10).
        # We trigger 7 days early: scheduled absolute day - 7 = day 14 (11 + 3).
        # So planting date must be 14 days ago.
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=14)
        )
        
        # Verify growth stage is vegetative
        self.assertEqual(crop.growth_stage, 'vegetative')
        
        # Generate reminders
        reminders = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders), 1)
        
        # Verify notification details
        notif = reminders[0]
        self.assertEqual(notif.priority, 'low')
        self.assertIn('(In 7 Days)', notif.title)
        self.assertFalse(notif.is_completed)

    def test_scheduled_today_escalation(self):
        """Test that on the scheduled day, the advance notification escalates to Today and Urgent"""
        from crops.services.reminder_service import CropReminderService
        from notifications.models import Notification
        
        today = date.today()
        
        # Create crop planted 14 days ago (triggered advance reminder)
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=14)
        )
        
        # Trigger advance reminder
        reminders = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders), 1)
        notif = reminders[0]
        self.assertEqual(notif.priority, 'low')
        
        # Now simulate passage of time: today becomes day 10 of vegetative stage (absolute day 21)
        Crop.objects.filter(id=crop.id).update(planting_date=today - timedelta(days=21))
        
        # Refresh from database and generate reminders again
        crop.refresh_from_db()
        reminders2 = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders2), 1)
        
        # Verify existing notification was updated
        updated_notif = Notification.objects.get(id=notif.id)
        self.assertEqual(updated_notif.priority, 'urgent')
        self.assertIn('(Scheduled Today)', updated_notif.title)
        self.assertFalse(updated_notif.is_completed)

    def test_overdue_escalation(self):
        """Test that past the scheduled day, an uncompleted notification escalates to Overdue and Critical"""
        from crops.services.reminder_service import CropReminderService
        from notifications.models import Notification
        
        today = date.today()
        
        # Create crop
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=14)
        )
        
        # Trigger advance reminder
        reminders = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders), 1)
        notif = reminders[0]
        
        # Now simulate time: today becomes absolute day 25 (overdue by 4 days)
        Crop.objects.filter(id=crop.id).update(planting_date=today - timedelta(days=25))
        
        # Refresh and generate
        crop.refresh_from_db()
        reminders2 = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders2), 1)
        
        # Verify existing notification was escalated to critical and overdue
        updated_notif = Notification.objects.get(id=notif.id)
        self.assertEqual(updated_notif.priority, 'critical')
        self.assertIn('(Overdue)', updated_notif.title)
        self.assertFalse(updated_notif.is_completed)

    def test_completion_stops_reminders(self):
        """Test that marking a notification as completed stops any further reminders or escalations"""
        from crops.services.reminder_service import CropReminderService
        from notifications.models import Notification
        
        today = date.today()
        
        # Create crop
        crop = Crop.objects.create(
            farmer=self.user,
            name='Paddy',
            variety='Basmati',
            field_name='North Field',
            field_area=1.5,
            planting_date=today - timedelta(days=14)
        )
        
        # Trigger advance reminder
        reminders = CropReminderService.generate_reminders_for_crop(crop)
        self.assertEqual(len(reminders), 1)
        notif = reminders[0]
        
        # Farmer marks it as completed
        notif.mark_as_completed()
        self.assertTrue(notif.is_completed)
        self.assertIsNotNone(notif.completed_at)
        
        # Now simulate time: today becomes absolute day 21 (scheduled today)
        Crop.objects.filter(id=crop.id).update(planting_date=today - timedelta(days=21))
        
        # Refresh and generate
        crop.refresh_from_db()
        reminders2 = CropReminderService.generate_reminders_for_crop(crop)
        
        # Since it is completed, it should NOT trigger or update
        self.assertEqual(len(reminders2), 0)
        
        # Verify the database notification remains completed and is not changed
        db_notif = Notification.objects.get(id=notif.id)
        self.assertTrue(db_notif.is_completed)
        self.assertEqual(db_notif.priority, 'low')
