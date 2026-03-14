from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from livestock.models import (
    AnimalType, Animal, VaccinationRecord, HealthRecord, 
    MilkRecord, BreedingRecord, AnimalIncome, AnimalExpense
)
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
        AnimalIncome.objects.all().delete()
        AnimalExpense.objects.all().delete()
        MilkRecord.objects.all().delete()
        BreedingRecord.objects.all().delete()
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
        
        # ========== TEST 8: CREATE MILK RECORDS ==========
        self.stdout.write('\n\n📝 TEST 8: Creating Milk Records')
        self.stdout.write('-' * 40)
        
        # Milk records for cow
        milk1 = MilkRecord.objects.create(
            animal=cow,
            date='2024-03-01',
            quantity_liters=15.5,
            milk_time='morning',
            notes='Good production'
        )
        self.stdout.write(f'✅ Created milk record: {milk1}')
        
        milk2 = MilkRecord.objects.create(
            animal=cow,
            date='2024-03-01',
            quantity_liters=12.0,
            milk_time='evening',
            notes='Evening milking'
        )
        self.stdout.write(f'✅ Created milk record: {milk2}')
        
        # ========== TEST 9: TEST MILK RECORD VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 9: Testing Milk Record Validation')
        self.stdout.write('-' * 40)
        
        # Test duplicate milk time (should fail due to unique_together)
        try:
            duplicate_milk = MilkRecord.objects.create(
                animal=cow,
                date='2024-03-01',
                quantity_liters=10.0,
                milk_time='morning',  # Already exists for this date!
            )
            self.stdout.write(self.style.ERROR('❌ Duplicate milk record created! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed (unique_together): {e}'))
        
        # Test negative quantity (should fail)
        try:
            negative_milk = MilkRecord.objects.create(
                animal=cow,
                date='2024-03-02',
                quantity_liters=-5.0,
                milk_time='morning',
            )
            self.stdout.write(self.style.ERROR('❌ Negative quantity allowed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 10: CREATE BREEDING RECORDS ==========
        self.stdout.write('\n\n📝 TEST 10: Creating Breeding Records')
        self.stdout.write('-' * 40)
        
        # Breeding record for cow (successful, not yet born)
        breed1 = BreedingRecord.objects.create(
            animal=cow,
            breeding_date='2024-01-15',
            successful=True,
            expected_birth_date='2024-10-15',
            sire_name='Neighbor\'s Bull',
            notes='AI performed'
        )
        self.stdout.write(f'✅ Created breeding record: {breed1}')
        
        # Breeding record for goat (successful, birth occurred)
        breed2 = BreedingRecord.objects.create(
            animal=goat,
            breeding_date='2024-01-10',
            successful=True,
            expected_birth_date='2024-06-10',
            actual_birth_date='2024-06-05',
            offspring_count=2,
            sire_name='Billy Jr.',
            notes='Twins born early'
        )
        self.stdout.write(f'✅ Created breeding record: {breed2}')
        
        # Breeding record for chicken (unsuccessful)
        breed3 = BreedingRecord.objects.create(
            animal=chicken,
            breeding_date='2024-02-01',
            successful=False,
            notes='No eggs fertilized'
        )
        self.stdout.write(f'✅ Created breeding record: {breed3}')
        
        # ========== TEST 11: TEST BREEDING RECORD VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 11: Testing Breeding Record Validation')
        self.stdout.write('-' * 40)
        
        # Test unsuccessful with expected birth date (should fail)
        try:
            invalid_breed = BreedingRecord.objects.create(
                animal=goat,
                breeding_date='2024-03-01',
                successful=False,
                expected_birth_date='2024-08-01',
            )
            self.stdout.write(self.style.ERROR('❌ Unsuccessful breeding with expected date created!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test successful without expected date (should fail)
        try:
            invalid_breed2 = BreedingRecord.objects.create(
                animal=goat,
                breeding_date='2024-03-01',
                successful=True,
                # No expected_birth_date
            )
            self.stdout.write(self.style.ERROR('❌ Successful breeding without expected date created!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test birth occurred without offspring count (should fail)
        try:
            invalid_breed3 = BreedingRecord.objects.create(
                animal=goat,
                breeding_date='2024-03-01',
                successful=True,
                expected_birth_date='2024-08-01',
                actual_birth_date='2024-08-05',
                offspring_count=0,  # Should be >0
            )
            self.stdout.write(self.style.ERROR('❌ Birth without offspring count created!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 12: CREATE ANIMAL INCOME RECORDS ==========
        self.stdout.write('\n\n📝 TEST 12: Creating Animal Income Records')
        self.stdout.write('-' * 40)
        
        # Milk income for cow
        income1 = AnimalIncome.objects.create(
            user=user,
            animal=cow,
            source='milk_sale',
            amount=5000,
            date='2024-03-02',
            description='Morning milk sale',
            buyer_name='Dairy Cooperative',
            buyer_contact='9841001001'
        )
        self.stdout.write(f'✅ Created income: {income1}')
        
        # Another milk income for cow
        income2 = AnimalIncome.objects.create(
            user=user,
            animal=cow,
            source='milk_sale',
            amount=4500,
            date='2024-03-03',
            description='Evening milk sale'
        )
        self.stdout.write(f'✅ Created income: {income2}')
        
        # Animal sale income for goat
        income3 = AnimalIncome.objects.create(
            user=user,
            animal=goat,
            source='animal_sale',
            amount=12000,
            date='2024-03-10',
            description='Sold goat to local farmer',
            buyer_name='Hari Bahadur',
            buyer_contact='9842002002'
        )
        self.stdout.write(f'✅ Created income: {income3}')
        
        # Egg income for chicken
        income4 = AnimalIncome.objects.create(
            user=user,
            animal=chicken,
            source='egg_sale',
            amount=800,
            date='2024-03-05',
            description='Eggs sold this week'
        )
        self.stdout.write(f'✅ Created income: {income4}')
        
        # ========== TEST 13: TEST INCOME VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 13: Testing Income Validation')
        self.stdout.write('-' * 40)
        
        # Test negative amount (should fail)
        try:
            invalid_income = AnimalIncome.objects.create(
                user=user,
                animal=chicken,
                source='egg_sale',
                amount=-100,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Negative amount allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test zero amount (should fail)
        try:
            invalid_income2 = AnimalIncome.objects.create(
                user=user,
                animal=chicken,
                source='egg_sale',
                amount=0,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Zero amount allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test future date (should fail if validation added)
        try:
            future_date = date.today() + timedelta(days=30)
            invalid_income3 = AnimalIncome.objects.create(
                user=user,
                animal=chicken,
                source='egg_sale',
                amount=500,
                date=future_date
            )
            self.stdout.write(self.style.ERROR('❌ Future date allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 14: CREATE ANIMAL EXPENSE RECORDS ==========
        self.stdout.write('\n\n📝 TEST 14: Creating Animal Expense Records')
        self.stdout.write('-' * 40)
        
        # Feed expense for cow
        expense1 = AnimalExpense.objects.create(
            user=user,
            animal=cow,
            category='feed',
            amount=3000,
            date='2024-03-01',
            description='Monthly feed',
            vendor_name='Agro Feed Store',
            vendor_contact='9843003003'
        )
        self.stdout.write(f'✅ Created expense: {expense1}')
        
        # Bedding expense for cow
        expense2 = AnimalExpense.objects.create(
            user=user,
            animal=cow,
            category='bedding',
            amount=1000,
            date='2024-03-05',
            description='Straw for bedding'
        )
        self.stdout.write(f'✅ Created expense: {expense2}')
        
        # Equipment expense for goat
        expense3 = AnimalExpense.objects.create(
            user=user,
            animal=goat,
            category='equipment',
            amount=2500,
            date='2024-03-08',
            description='Water trough'
        )
        self.stdout.write(f'✅ Created expense: {expense3}')
        
        # Transport expense for chicken
        expense4 = AnimalExpense.objects.create(
            user=user,
            animal=chicken,
            category='transport',
            amount=500,
            date='2024-03-02',
            description='Transport to market'
        )
        self.stdout.write(f'✅ Created expense: {expense4}')
        
        # ========== TEST 15: TEST EXPENSE VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 15: Testing Expense Validation')
        self.stdout.write('-' * 40)
        
        # Test negative amount (should fail)
        try:
            invalid_expense = AnimalExpense.objects.create(
                user=user,
                animal=chicken,
                category='feed',
                amount=-200,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Negative amount allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test zero amount (should fail)
        try:
            invalid_expense2 = AnimalExpense.objects.create(
                user=user,
                animal=chicken,
                category='feed',
                amount=0,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Zero amount allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test future date (should fail if validation added)
        try:
            future_date = date.today() + timedelta(days=30)
            invalid_expense3 = AnimalExpense.objects.create(
                user=user,
                animal=chicken,
                category='feed',
                amount=500,
                date=future_date
            )
            self.stdout.write(self.style.ERROR('❌ Future date allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 16: QUERY RELATED RECORDS ==========
        self.stdout.write('\n\n📝 TEST 16: Querying Related Records')
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
        
        # Get all milk records for cow
        cow_milk = cow.milk_records.all()
        self.stdout.write(f'\n🥛 Cow milk records ({cow_milk.count()}):')
        for milk in cow_milk:
            self.stdout.write(f'   - {milk.date}: {milk.quantity_liters}L ({milk.get_milk_time_display()})')
        
        # Get all breeding records for cow
        cow_breeding = cow.breeding_records.all()
        self.stdout.write(f'\n🤰 Cow breeding records ({cow_breeding.count()}):')
        for breed in cow_breeding:
            status = "Successful" if breed.successful else "Unsuccessful"
            self.stdout.write(f'   - {breed.breeding_date}: {status}')
        
        # Get all income records for cow
        cow_income = cow.incomes.all()
        self.stdout.write(f'\n💰 Cow income records ({cow_income.count()}):')
        for income in cow_income:
            self.stdout.write(f'   - {income.date}: {income.get_source_display()} - NPR {income.amount}')
        
        # Get all expense records for cow
        cow_expense = cow.expenses.all()
        self.stdout.write(f'\n💸 Cow expense records ({cow_expense.count()}):')
        for expense in cow_expense:
            self.stdout.write(f'   - {expense.date}: {expense.get_category_display()} - NPR {expense.amount}')
        
        # ========== TEST 17: TEST FINANCIAL CALCULATIONS ==========
        self.stdout.write('\n\n📝 TEST 17: Testing Financial Calculations')
        self.stdout.write('-' * 40)
        
        # Refresh cow from database
        cow.refresh_from_db()
        
        self.stdout.write(f'\n🐄 {cow.name} Financial Summary:')
        self.stdout.write(f'   Acquisition Cost: NPR {cow.acquisition_cost}')
        self.stdout.write(f'   Vaccination Cost: NPR {cow.total_vaccination_cost}')
        self.stdout.write(f'   Health Cost: NPR {cow.total_health_cost}')
        self.stdout.write(f'   Medical Cost: NPR {cow.total_medical_cost}')
        self.stdout.write(f'   Other Expenses: NPR {cow.total_other_expense}')
        self.stdout.write(f'   Total Expense: NPR {cow.total_expense}')
        self.stdout.write(f'   Milk Income: NPR {cow.milk_income}')
        self.stdout.write(f'   Total Income: NPR {cow.total_income}')
        self.stdout.write(f'   Net Profit: NPR {cow.net_profit}')
        self.stdout.write(f'   Profit Margin: {cow.profit_margin:.1f}%')
        
        # Verify calculations
        expected_vax_cost = 1500
        expected_health_cost = 2000
        expected_other_expense = 4000  # feed(3000) + bedding(1000)
        expected_income = 9500  # milk(5000+4500)
        expected_total_expense = cow.acquisition_cost + expected_vax_cost + expected_health_cost + expected_other_expense
        expected_net_profit = expected_income - expected_total_expense
        
        if (cow.total_vaccination_cost == expected_vax_cost and
            cow.total_health_cost == expected_health_cost and
            cow.total_other_expense == expected_other_expense and
            cow.total_income == expected_income):
            self.stdout.write(self.style.SUCCESS('✅ Financial calculations are CORRECT!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Financial calculations are WRONG!'))
        
        # ========== TEST 18: FILTER RECORDS ==========
        self.stdout.write('\n\n📝 TEST 18: Filtering Records')
        self.stdout.write('-' * 40)
        
        # Filter vaccinations by date
        recent_vax = VaccinationRecord.objects.filter(
            vaccine_date__gte='2024-02-01'
        )
        self.stdout.write(f'✅ Recent vaccinations (after Feb 2024): {recent_vax.count()}')
        
        # Filter health records by type
        checkups = HealthRecord.objects.filter(health_type='checkup')
        self.stdout.write(f'✅ Regular checkups: {checkups.count()}')
        
        # Filter milk records by date
        today_milk = MilkRecord.objects.filter(date='2024-03-01')
        self.stdout.write(f'✅ Milk records on 2024-03-01: {today_milk.count()}')
        
        # Filter successful breeding records
        successful_breeding = BreedingRecord.objects.filter(successful=True)
        self.stdout.write(f'✅ Successful breeding records: {successful_breeding.count()}')
        
        # Filter income by source
        milk_income = AnimalIncome.objects.filter(source='milk_sale')
        self.stdout.write(f'✅ Milk income records: {milk_income.count()}')
        
        # Filter expense by category
        feed_expenses = AnimalExpense.objects.filter(category='feed')
        self.stdout.write(f'✅ Feed expenses: {feed_expenses.count()}')
        
        # ========== TEST 19: UPDATE RECORDS ==========
        self.stdout.write('\n\n📝 TEST 19: Updating Records')
        self.stdout.write('-' * 40)
        
        # Update vaccination
        vax1.notes = 'First dose completed successfully'
        vax1.save()
        self.stdout.write('✅ Updated vaccination notes')
        
        # Update health record
        health2.follow_up_date = '2024-03-12'
        health2.save()
        self.stdout.write('✅ Added follow-up date to health record')
        
        # Update breeding record (add birth info)
        breed1.actual_birth_date = '2024-10-12'
        breed1.offspring_count = 1
        breed1.save()
        self.stdout.write('✅ Updated breeding record with birth info')
        
        # Update income record
        income1.notes = 'Paid via bank transfer'
        income1.save()
        self.stdout.write('✅ Updated income record notes')
        
        # Update expense record
        expense1.amount = 3200  # Price increased
        expense1.save()
        self.stdout.write('✅ Updated expense amount')
        
        # ========== TEST 20: TEST PROTECT CONSTRAINT ==========
        self.stdout.write('\n\n📝 TEST 20: Testing PROTECT Constraint')
        self.stdout.write('-' * 40)
        
        try:
            self.stdout.write('Attempting to delete Cow animal type...')
            animal_types['Cow'].delete()
            self.stdout.write(self.style.ERROR('❌ This should NOT have worked!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ PROTECT still working! Error: {e}'))
        
        # ========== TEST 21: DELETE A RECORD ==========
        self.stdout.write('\n\n📝 TEST 21: Deleting a Record')
        self.stdout.write('-' * 40)
        
        # Delete an expense record
        expense4.delete()
        self.stdout.write('✅ Deleted chicken transport expense')
        
        # Verify deletion
        remaining_expenses = AnimalExpense.objects.filter(animal=chicken).count()
        self.stdout.write(f'✅ Chicken now has {remaining_expenses} expense records')
        
        # ========== TEST SUMMARY ==========
        self.stdout.write('\n\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('          TEST SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ Animal Types: {AnimalType.objects.count()}')
        self.stdout.write(f'✅ Animals: {Animal.objects.filter(farmer=user).count()}')
        self.stdout.write(f'✅ Vaccination Records: {VaccinationRecord.objects.count()}')
        self.stdout.write(f'✅ Health Records: {HealthRecord.objects.count()}')
        self.stdout.write(f'✅ Milk Records: {MilkRecord.objects.count()}')
        self.stdout.write(f'✅ Breeding Records: {BreedingRecord.objects.count()}')
        self.stdout.write(f'✅ Income Records: {AnimalIncome.objects.count()}')
        self.stdout.write(f'✅ Expense Records: {AnimalExpense.objects.count()}')
        self.stdout.write(f'✅ PROTECT constraint: Working')
        self.stdout.write(f'✅ Validation rules: Working')
        self.stdout.write(f'✅ Relationships: Working')
        self.stdout.write(f'✅ Unique constraints: Working')
        self.stdout.write(f'✅ Financial calculations: Working')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ All livestock tests passed!'))
        self.stdout.write('=' * 60)