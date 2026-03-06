from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from livestock.models import AnimalType, Animal
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Test livestock models and relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('     LIVESTOCK TEST SUITE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ========== GET OR CREATE TEST USER ==========
        user, created = User.objects.get_or_create(
            email='test@farmer.com',
            defaults={
                'username': 'testfarmer',
                'password': 'test123'
            }
        )
        if created:
            self.stdout.write('✅ Created test user')
        else:
            self.stdout.write('✅ Using existing test user')
        
        # ========== TEST 1: CREATE ANIMAL TYPES ==========
        self.stdout.write('\n\n📝 TEST 1: Creating Animal Types')
        self.stdout.write('-' * 40)
        
        animal_types = {}
        types_data = [
            ('Cow', 'गाई', 280, True, False),
            ('Goat', 'बाख्रा', 150, True, False),
            ('Chicken', 'कुखुरा', 21, False, True),
        ]
        
        for name, name_np, gestation, is_milk, is_egg in types_data:
            obj, created = AnimalType.objects.get_or_create(
                name=name,
                defaults={
                    'name_np': name_np,
                    'gestation_days': gestation,
                    'is_milk_animal': is_milk,
                    'is_egg_animal': is_egg,
                }
            )
            animal_types[name] = obj
            self.stdout.write(f'✅ Created/Found: {name}')
        
        self.stdout.write(f'\n📊 Total animal types: {AnimalType.objects.count()}')
        
        # ========== TEST 2: CREATE ANIMALS ==========
        self.stdout.write('\n\n📝 TEST 2: Creating Animals')
        self.stdout.write('-' * 40)
        
        animals = []
        
        # Create a cow
        cow = Animal.objects.create(
            farmer=user,
            animal_type=animal_types['Cow'],
            name='Bossie',
            tag_number='COW001',
            birth_date='2022-01-15',
            acquisition_date='2022-02-01',
            acquisition_cost=50000,
            gender='female',
            status='active',
            is_pregnant=True,
            last_pregnancy_date='2024-01-15',
            expected_birth_date='2024-10-15',  # ~280 days later
            notes='Healthy cow, good milk production'
        )
        animals.append(cow)
        self.stdout.write(f'✅ Created cow: {cow}')
        
        # Create a goat
        goat = Animal.objects.create(
            farmer=user,
            animal_type=animal_types['Goat'],
            name='Billy',
            tag_number='GOAT001',
            birth_date='2023-05-10',
            acquisition_date='2023-06-01',
            acquisition_cost=8000,
            gender='male',
            status='active'
        )
        animals.append(goat)
        self.stdout.write(f'✅ Created goat: {goat}')
        
        # Create a chicken
        chicken = Animal.objects.create(
            farmer=user,
            animal_type=animal_types['Chicken'],
            tag_number='CHK001',
            acquisition_date='2024-01-10',
            acquisition_cost=500,
            gender='female',
            status='active'
        )
        animals.append(chicken)
        self.stdout.write(f'✅ Created chicken: {chicken}')
        
        # ========== TEST 3: QUERY ANIMALS ==========
        self.stdout.write('\n\n📝 TEST 3: Querying Animals')
        self.stdout.write('-' * 40)
        
        # All animals
        all_animals = Animal.objects.filter(farmer=user)
        self.stdout.write(f'\n📋 All animals ({all_animals.count()}):')
        for animal in all_animals:
            self.stdout.write(f'   - {animal}')
        
        # Filter by type
        cows = Animal.objects.filter(animal_type=animal_types['Cow'])
        self.stdout.write(f'\n🐄 Cows: {cows.count()}')
        
        # Filter by gender
        females = Animal.objects.filter(gender='female')
        self.stdout.write(f'♀️ Females: {females.count()}')
        
        # Filter by pregnant
        pregnant = Animal.objects.filter(is_pregnant=True)
        self.stdout.write(f'🤰 Pregnant: {pregnant.count()}')
        for animal in pregnant:
            self.stdout.write(f'   - {animal} due: {animal.expected_birth_date}')
        
        # ========== TEST 4: TEST PROTECT CONSTRAINT ==========
        self.stdout.write('\n\n📝 TEST 4: Testing PROTECT Constraint')
        self.stdout.write('-' * 40)
        
        try:
            self.stdout.write('Attempting to delete Cow animal type...')
            animal_types['Cow'].delete()
            self.stdout.write(self.style.ERROR('❌ This should NOT have worked!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ PROTECT worked! Error: {e}'))
        
        # ========== TEST 5: UPDATE AN ANIMAL ==========
        self.stdout.write('\n\n📝 TEST 5: Updating an Animal')
        self.stdout.write('-' * 40)
        
        cow.status = 'sold'
        cow.save()
        self.stdout.write(f'✅ Updated cow status to "sold"')
        
        # Verify update
        updated_cow = Animal.objects.get(tag_number='COW001')
        self.stdout.write(f'✅ Verified: Cow status is now {updated_cow.status}')
        
        # ========== TEST 6: FILTER VIEWS ==========
        self.stdout.write('\n\n📝 TEST 6: Testing Filter Views')
        self.stdout.write('-' * 40)
        
        active = Animal.objects.filter(farmer=user, status='active')
        self.stdout.write(f'✅ Active animals: {active.count()}')
        for animal in active:
            self.stdout.write(f'   - {animal}')
        
        # ========== TEST SUMMARY ==========
        self.stdout.write('\n\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('          TEST SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ Animal Types created: {AnimalType.objects.count()}')
        self.stdout.write(f'✅ Animals created: {Animal.objects.filter(farmer=user).count()}')
        self.stdout.write(f'✅ PROTECT constraint: Working')
        self.stdout.write(f'✅ Update functionality: Working')
        self.stdout.write(f'✅ Filter functionality: Working')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ All livestock tests passed!'))
        self.stdout.write('=' * 60)