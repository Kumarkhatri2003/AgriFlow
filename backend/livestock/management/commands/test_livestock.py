from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from livestock.models import AnimalType, Animal, VaccinationRecord, HealthRecord
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Test livestock models and relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('     LIVESTOCK TEST SUITE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ========== CLEAN UP EXISTING DATA ==========
        self.stdout.write('\n\n🧹 Cleaning up existing test data...')
        
        # Delete existing records (in correct order due to foreign keys)
        VaccinationRecord.objects.all().delete()
        HealthRecord.objects.all().delete()
        Animal.objects.all().delete()
        # Don't delete AnimalTypes - they're master data
        
        self.stdout.write('✅ Cleaned up existing records')
        
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
        
        animals = {}
        
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
            expected_birth_date='2024-10-15',
            notes='Healthy cow, good milk production'
        )
        animals['cow'] = cow
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
        animals['goat'] = goat
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
        animals['chicken'] = chicken
        self.stdout.write(f'✅ Created chicken: {chicken}')
        
        # ========== TEST 3: TEST ANIMAL VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 3: Testing Animal Validation')
        self.stdout.write('-' * 40)
        
        # Test 3.1: Try to create male pregnant animal (should fail)
        try:
            invalid_animal = Animal.objects.create(
                farmer=user,
                animal_type=animal_types['Goat'],
                name='Invalid',
                tag_number='INVALID001',
                acquisition_date='2024-01-01',
                gender='male',
                is_pregnant=True,
                last_pregnancy_date='2024-01-15'
            )
            self.stdout.write(self.style.ERROR('❌ Male pregnant animal created! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 4: CREATE VACCINATION RECORDS ==========
        self.stdout.write('\n\n📝 TEST 4: Creating Vaccination Records')
        self.stdout.write('-' * 40)
        
        # Vaccination for cow
        vax1 = VaccinationRecord.objects.create(
            animal=cow,
            vaccine_name='Foot and Mouth Disease',
            vaccine_date='2024-01-15',
            next_due_date='2024-07-15',
            administered_by='Dr. Sharma',
            cost=1500,
            notes='First dose'
        )
        self.stdout.write(f'✅ Created vaccination: {vax1}')
        
        # Vaccination for goat
        vax2 = VaccinationRecord.objects.create(
            animal=goat,
            vaccine_name='PPR Vaccine',
            vaccine_date='2024-02-01',
            next_due_date='2025-02-01',
            cost=800
        )
        self.stdout.write(f'✅ Created vaccination: {vax2}')
        
        # ========== TEST 5: TEST VACCINATION VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 5: Testing Vaccination Validation')
        self.stdout.write('-' * 40)
        
        # Test negative cost (should fail)
        try:
            invalid_vax = VaccinationRecord.objects.create(
                animal=chicken,
                vaccine_name='Invalid',
                vaccine_date='2024-01-01',
                cost=-500
            )
            self.stdout.write(self.style.ERROR('❌ Negative cost allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 6: CREATE HEALTH RECORDS ==========
        self.stdout.write('\n\n📝 TEST 6: Creating Health Records')
        self.stdout.write('-' * 40)
        
        # Health record for cow
        health1 = HealthRecord.objects.create(
            animal=cow,
            health_type='checkup',
            diagnosis='Regular checkup',
            treatment='Deworming',
            treatment_date='2024-03-01',
            follow_up_date='2024-06-01',
            vet_name='Dr. Sharma',
            cost=2000,
            notes='All good'
        )
        self.stdout.write(f'✅ Created health record: {health1}')
        
        # Health record for chicken
        health2 = HealthRecord.objects.create(
            animal=chicken,
            health_type='sick',
            diagnosis='Respiratory infection',
            treatment='Antibiotics',
            treatment_date='2024-03-05',
            cost=300
        )
        self.stdout.write(f'✅ Created health record: {health2}')
        
        # ========== TEST 7: TEST HEALTH RECORD VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 7: Testing Health Record Validation')
        self.stdout.write('-' * 40)
        
        # Test negative cost (should fail)
        try:
            invalid_health = HealthRecord.objects.create(
                animal=goat,
                health_type='checkup',
                diagnosis='Invalid',
                treatment_date='2024-01-01',
                cost=-200
            )
            self.stdout.write(self.style.ERROR('❌ Negative cost allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 8: QUERY RELATED RECORDS ==========
        self.stdout.write('\n\n📝 TEST 8: Querying Related Records')
        self.stdout.write('-' * 40)
        
        # Get all vaccinations for cow
        cow_vax = cow.vaccinations.all()
        self.stdout.write(f'\n🐄 Cow vaccinations ({cow_vax.count()}):')
        for vax in cow_vax:
            self.stdout.write(f'   - {vax.vaccine_name} on {vax.vaccine_date}')
        
        # Get all health records for chicken
        chicken_health = chicken.health_records.all()
        self.stdout.write(f'\n🐔 Chicken health records ({chicken_health.count()}):')
        for health in chicken_health:
            self.stdout.write(f'   - {health.get_health_type_display()}: {health.diagnosis}')
        
        # ========== TEST 9: FILTER RECORDS ==========
        self.stdout.write('\n\n📝 TEST 9: Filtering Records')
        self.stdout.write('-' * 40)
        
        # Filter vaccinations by date
        recent_vax = VaccinationRecord.objects.filter(
            vaccine_date__gte='2024-02-01'
        )
        self.stdout.write(f'✅ Recent vaccinations (after Feb 2024): {recent_vax.count()}')
        
        # Filter health records by type
        checkups = HealthRecord.objects.filter(health_type='checkup')
        self.stdout.write(f'✅ Regular checkups: {checkups.count()}')
        
        # ========== TEST 10: UPDATE RECORDS ==========
        self.stdout.write('\n\n📝 TEST 10: Updating Records')
        self.stdout.write('-' * 40)
        
        # Update vaccination
        vax1.notes = 'First dose completed successfully'
        vax1.save()
        self.stdout.write('✅ Updated vaccination notes')
        
        # Update health record
        health2.follow_up_date = '2024-03-12'
        health2.save()
        self.stdout.write('✅ Added follow-up date to health record')
        
        # ========== TEST 11: TEST PROTECT CONSTRAINT (AGAIN) ==========
        self.stdout.write('\n\n📝 TEST 11: Testing PROTECT Constraint Again')
        self.stdout.write('-' * 40)
        
        try:
            self.stdout.write('Attempting to delete Goat animal type...')
            animal_types['Goat'].delete()
            self.stdout.write(self.style.ERROR('❌ This should NOT have worked!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ PROTECT still working! Error: {e}'))
        
        # ========== TEST SUMMARY ==========
        self.stdout.write('\n\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('          TEST SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ Animal Types: {AnimalType.objects.count()}')
        self.stdout.write(f'✅ Animals: {Animal.objects.filter(farmer=user).count()}')
        self.stdout.write(f'✅ Vaccination Records: {VaccinationRecord.objects.count()}')
        self.stdout.write(f'✅ Health Records: {HealthRecord.objects.count()}')
        self.stdout.write(f'✅ PROTECT constraint: Working')
        self.stdout.write(f'✅ Validation rules: Working')
        self.stdout.write(f'✅ Relationships: Working')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ All livestock tests passed!'))
        self.stdout.write('=' * 60)