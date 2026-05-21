from django.core.management.base import BaseCommand
from livestock.alert_generator import LivestockAlertGenerator


class Command(BaseCommand):
    help = 'Generate daily alerts for livestock'

    def handle(self, *args, **kwargs):
        count = LivestockAlertGenerator.generate_all_alerts()
        self.stdout.write(self.style.SUCCESS(f"Generated {count} livestock alerts for today"))