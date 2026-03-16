from django.core.management.base import BaseCommand
from livestock.models import AnimalType

class Command(BaseCommand):
    help = 'Load default animal types'

    def handle(self, *args, **options):
        animal_types = [
            # (name, name_np, gestation_days, is_milk, is_egg)
            ('Cow', 'गाई', 280, True, False),
            ('Buffalo', 'भैंसी', 310, True, False),
            ('Goat', 'बाख्रा', 150, True, False),
            ('Sheep', 'भेडा', 147, True, False),
            ('Pig', 'सुँगुर', 114, False, False),
            ('Chicken', 'कुखुरा', 21, False, True),
            ('Duck', 'हाँस', 28, False, True),
            ('Horse', 'घोडा', 340, False, False),
            ('Donkey', 'गधा', 365, False, False),
            ('Rabbit', 'खरायो', 31, False, False),
        ]
        
        created_count = 0
        for name, name_np, gestation, is_milk, is_egg in animal_types:
            obj, created = AnimalType.objects.get_or_create(
                name=name,
                defaults={
                    'name_np': name_np,
                    'gestation_days': gestation,
                    'is_milk_animal': is_milk,
                    'is_egg_animal': is_egg,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"✅ Added {name}")
            else:
                self.stdout.write(f"⏩ {name} already exists")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully added {created_count} animal types'))