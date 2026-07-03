# crops/management/commands/generate_crop_reminders.py

from django.core.management.base import BaseCommand
from crops.services.reminder_service import CropReminderService


class Command(BaseCommand):
    help = 'Generate daily crop activity reminders for all active crops'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--crop-id',
            type=str,
            help='Generate reminders for specific crop only'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("[CROP] Generating crop activity reminders...")
        self.stdout.write("-" * 40)
        
        if options['crop_id']:
            from crops.models import Crop
            try:
                crop = Crop.objects.get(id=options['crop_id'], status='active')
                reminders = CropReminderService.generate_reminders_for_crop(crop)
                self.stdout.write(self.style.SUCCESS(
                    f"\n✅ Generated {len(reminders)} reminders for {crop.name}"
                ))
            except Crop.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Crop {options['crop_id']} not found"))
        else:
            results = CropReminderService.generate_reminders_for_all_crops()
            
            self.stdout.write(f"\n📊 Summary:")
            self.stdout.write(f"   • Active crops: {results['total_crops']}")
            self.stdout.write(f"   • Reminders generated: {results['total_reminders']}")
            
            if results['details']:
                self.stdout.write(f"\n📋 Details:")
                for detail in results['details']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"   ✓ {detail['crop_name']} ({detail['farmer']}): {detail['reminders']} reminders"
                        )
                    )
            else:
                self.stdout.write(self.style.WARNING("\n   No reminders generated today"))
        
        self.stdout.write("\n✅ Done!")