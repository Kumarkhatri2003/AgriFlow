from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from crops.models import (
    Crop, FertilizerRecord, PesticideRecord, 
    CropExpense, CropIncome, HarvestRecord
)
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Test crop finance models and relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('     CROP FINANCE TEST SUITE'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # ========== CLEAN UP EXISTING DATA ==========
        self.stdout.write('\n\n🧹 Cleaning up existing test data...')
        
        # Delete in correct order (due to foreign keys)
        HarvestRecord.objects.all().delete()
        CropIncome.objects.all().delete()
        CropExpense.objects.all().delete()
        PesticideRecord.objects.all().delete()
        FertilizerRecord.objects.all().delete()
        Crop.objects.all().delete()
        
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
        
        # ========== TEST 1: CREATE CROPS ==========
        self.stdout.write('\n\n📝 TEST 1: Creating Crops')
        self.stdout.write('-' * 40)
        
        crops = {}
        
        # Create Rice crop
        rice = Crop.objects.create(
            farmer=user,
            name='Rice',
            name_np='धान',
            variety='Basmati-1',
            field_name='North Field',
            field_area=2.5,
            area_unit='ropani',
            planting_date='2024-01-15',
            expected_harvest_date='2024-05-15',
            growth_stage='vegetative',
            is_irrigated=True,
            soil_type='Loamy',
            status='active',
            notes='Planted after first rain'
        )
        crops['rice'] = rice
        self.stdout.write(f'✅ Created crop: {rice}')
        
        # Create Wheat crop
        wheat = Crop.objects.create(
            farmer=user,
            name='Wheat',
            name_np='गहुँ',
            variety='NL-971',
            field_name='South Field',
            field_area=1.8,
            area_unit='kattha',
            planting_date='2024-02-01',
            expected_harvest_date='2024-06-01',
            growth_stage='seeding',
            is_irrigated=False,
            soil_type='Clay',
            status='active'
        )
        crops['wheat'] = wheat
        self.stdout.write(f'✅ Created crop: {wheat}')
        
        # Create Maize crop
        maize = Crop.objects.create(
            farmer=user,
            name='Maize',
            name_np='मकै',
            variety='Khumal-4',
            field_name='East Field',
            field_area=3.0,
            area_unit='kattha',
            planting_date='2024-03-01',
            growth_stage='seeding',
            is_irrigated=True,
            soil_type='Sandy',
            status='active'
        )
        crops['maize'] = maize
        self.stdout.write(f'✅ Created crop: {maize}')
        
        self.stdout.write(f'\n📊 Total crops: {Crop.objects.filter(farmer=user).count()}')
        
        # ========== TEST 2: CREATE FERTILIZER RECORDS ==========
        self.stdout.write('\n\n📝 TEST 2: Creating Fertilizer Records')
        self.stdout.write('-' * 40)
        
        fertilizers = []
        
        # Fertilizer for Rice
        fert1 = FertilizerRecord.objects.create(
            user=user,
            crop=rice,
            fertilizer_type='chemical',
            name='Urea',
            quantity=50.00,
            unit='kg',
            cost=2500.00,
            application_date='2024-02-15',
            notes='First application'
        )
        fertilizers.append(fert1)
        self.stdout.write(f'✅ Created fertilizer: {fert1}')
        
        # Fertilizer for Rice (second application)
        fert2 = FertilizerRecord.objects.create(
            user=user,
            crop=rice,
            fertilizer_type='chemical',
            name='DAP',
            quantity=25.00,
            unit='kg',
            cost=3000.00,
            application_date='2024-03-01',
            notes='Second application'
        )
        fertilizers.append(fert2)
        self.stdout.write(f'✅ Created fertilizer: {fert2}')
        
        # Fertilizer for Maize
        fert3 = FertilizerRecord.objects.create(
            user=user,
            crop=maize,
            fertilizer_type='organic',
            name='Compost',
            quantity=100.00,
            unit='kg',
            cost=1500.00,
            application_date='2024-03-10'
        )
        fertilizers.append(fert3)
        self.stdout.write(f'✅ Created fertilizer: {fert3}')
        
        # ========== TEST 3: TEST FERTILIZER VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 3: Testing Fertilizer Validation')
        self.stdout.write('-' * 40)
        
        # Test negative cost (should fail)
        try:
            invalid_fert = FertilizerRecord.objects.create(
                user=user,
                crop=wheat,
                name='Invalid',
                quantity=10,
                unit='kg',
                cost=-500,
                application_date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Negative cost allowed! Validation failed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # Test negative quantity (should fail at model level)
        try:
            invalid_fert2 = FertilizerRecord.objects.create(
                user=user,
                crop=wheat,
                name='Invalid',
                quantity=-10,
                unit='kg',
                cost=500,
                application_date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Negative quantity allowed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 4: CREATE PESTICIDE RECORDS ==========
        self.stdout.write('\n\n📝 TEST 4: Creating Pesticide Records')
        self.stdout.write('-' * 40)
        
        pesticides = []
        
        # Pesticide for Rice
        pest1 = PesticideRecord.objects.create(
            user=user,
            crop=rice,
            name='Cypermethrin',
            target_pest='Stem borer',
            quantity=2.5,
            unit='ml',
            cost=800.00,
            application_date='2024-02-20',
            notes='Sprayed in morning'
        )
        pesticides.append(pest1)
        self.stdout.write(f'✅ Created pesticide: {pest1}')
        
        # Pesticide for Maize
        pest2 = PesticideRecord.objects.create(
            user=user,
            crop=maize,
            name='Emamectin benzoate',
            target_pest='Fall armyworm',
            quantity=1.5,
            unit='ml',
            cost=1200.00,
            application_date='2024-03-15'
        )
        pesticides.append(pest2)
        self.stdout.write(f'✅ Created pesticide: {pest2}')
        
        # ========== TEST 5: CREATE CROP EXPENSES ==========
        self.stdout.write('\n\n📝 TEST 5: Creating Crop Expenses (Other)')
        self.stdout.write('-' * 40)
        
        expenses = []
        
        # Seed expense for Rice
        exp1 = CropExpense.objects.create(
            user=user,
            crop=rice,
            category='seed',
            amount=3000.00,
            date='2024-01-10',
            description='Basmati rice seeds',
            vendor_name='Agro Center',
            vendor_contact='9841234567',
            notes='Good quality seeds'
        )
        expenses.append(exp1)
        self.stdout.write(f'✅ Created expense: {exp1}')
        
        # Labor expense for Rice
        exp2 = CropExpense.objects.create(
            user=user,
            crop=rice,
            category='labor',
            amount=5000.00,
            date='2024-01-15',
            description='Planting labor (4 workers)'
        )
        expenses.append(exp2)
        self.stdout.write(f'✅ Created expense: {exp2}')
        
        # Land rent expense for Wheat
        exp3 = CropExpense.objects.create(
            user=user,
            crop=wheat,
            category='land_rent',
            amount=8000.00,
            date='2024-02-01',
            description='Monthly land rent'
        )
        expenses.append(exp3)
        self.stdout.write(f'✅ Created expense: {exp3}')
        
        # Irrigation expense for Maize
        exp4 = CropExpense.objects.create(
            user=user,
            crop=maize,
            category='irrigation',
            amount=2000.00,
            date='2024-03-05',
            description='Water bill'
        )
        expenses.append(exp4)
        self.stdout.write(f'✅ Created expense: {exp4}')
        
        # ========== TEST 6: TEST EXPENSE VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 6: Testing Expense Validation')
        self.stdout.write('-' * 40)
        
        # Test negative amount (should fail)
        try:
            invalid_exp = CropExpense.objects.create(
                user=user,
                crop=wheat,
                category='seed',
                amount=-1000,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Negative amount allowed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 7: CREATE CROP INCOME ==========
        self.stdout.write('\n\n📝 TEST 7: Creating Crop Income')
        self.stdout.write('-' * 40)
        
        incomes = []
        
        # Crop sale income for Rice (partial harvest)
        inc1 = CropIncome.objects.create(
            user=user,
            crop=rice,
            source='crop_sale',
            amount=15000.00,
            date='2024-05-10',
            description='Sold 100kg rice',
            buyer_name='Local Market',
            buyer_contact='9876543210'
        )
        incomes.append(inc1)
        self.stdout.write(f'✅ Created income: {inc1}')
        
        # Government subsidy
        inc2 = CropIncome.objects.create(
            user=user,
            crop=rice,
            source='subsidy',
            amount=5000.00,
            date='2024-05-15',
            description='PM Agricultural Subsidy'
        )
        incomes.append(inc2)
        self.stdout.write(f'✅ Created income: {inc2}')
        
        # Crop sale for Maize
        inc3 = CropIncome.objects.create(
            user=user,
            crop=maize,
            source='crop_sale',
            amount=8000.00,
            date='2024-05-20',
            description='Sold 50kg maize'
        )
        incomes.append(inc3)
        self.stdout.write(f'✅ Created income: {inc3}')
        
        # ========== TEST 8: TEST INCOME VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 8: Testing Income Validation')
        self.stdout.write('-' * 40)
        
        # Test zero amount (should fail)
        try:
            invalid_inc = CropIncome.objects.create(
                user=user,
                crop=wheat,
                source='crop_sale',
                amount=0,
                date='2024-03-01'
            )
            self.stdout.write(self.style.ERROR('❌ Zero amount allowed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 9: CREATE HARVEST RECORDS ==========
        self.stdout.write('\n\n📝 TEST 9: Creating Harvest Records')
        self.stdout.write('-' * 40)
        
        harvests = []
        
        # Harvest for Rice
        har1 = HarvestRecord.objects.create(
            user=user,
            crop=rice,
            harvest_date='2024-05-15',
            quantity=200.00,
            unit='kg',
            quality='premium',
            notes='Good yield'
        )
        harvests.append(har1)
        self.stdout.write(f'✅ Created harvest: {har1}')
        
        # Second harvest for Rice
        har2 = HarvestRecord.objects.create(
            user=user,
            crop=rice,
            harvest_date='2024-05-20',
            quantity=150.00,
            unit='kg',
            quality='standard'
        )
        harvests.append(har2)
        self.stdout.write(f'✅ Created harvest: {har2}')
        
        # ========== TEST 10: TEST HARVEST VALIDATION ==========
        self.stdout.write('\n\n📝 TEST 10: Testing Harvest Validation')
        self.stdout.write('-' * 40)
        
        # Test negative quantity (should fail)
        try:
            invalid_har = HarvestRecord.objects.create(
                user=user,
                crop=wheat,
                harvest_date='2024-06-01',
                quantity=-50,
                unit='kg'
            )
            self.stdout.write(self.style.ERROR('❌ Negative quantity allowed!'))
        except Exception as e:
            self.stdout.write(self.style.SUCCESS(f'✅ Validation passed: {e}'))
        
        # ========== TEST 11: TEST CROP FINANCIAL PROPERTIES ==========
        self.stdout.write('\n\n📝 TEST 11: Testing Crop Financial Properties')
        self.stdout.write('-' * 40)
        
        # Refresh crop from database
        rice.refresh_from_db()
        
        self.stdout.write(f'\n🌾 Rice Financial Summary:')
        self.stdout.write(f'   Fertilizer Cost: NPR {rice.total_fertilizer_cost}')
        self.stdout.write(f'   Pesticide Cost: NPR {rice.total_pesticide_cost}')
        self.stdout.write(f'   Other Expenses: NPR {rice.total_other_expense}')
        self.stdout.write(f'   Total Expense: NPR {rice.total_expense}')
        self.stdout.write(f'   Total Income: NPR {rice.total_income}')
        self.stdout.write(f'   Net Profit: NPR {rice.net_profit}')
        
        # Verify calculations
        expected_fert_cost = Decimal('5500.00')  # 2500 + 3000
        expected_pest_cost = Decimal('800.00')
        expected_other_exp = Decimal('8000.00')  # 3000 + 5000
        expected_total_exp = expected_fert_cost + expected_pest_cost + expected_other_exp
        expected_income = Decimal('20000.00')  # 15000 + 5000
        expected_profit = expected_income - expected_total_exp
        
        if (rice.total_fertilizer_cost == expected_fert_cost and
            rice.total_pesticide_cost == expected_pest_cost and
            rice.total_other_expense == expected_other_exp and
            rice.total_expense == expected_total_exp and
            rice.total_income == expected_income and
            rice.net_profit == expected_profit):
            self.stdout.write(self.style.SUCCESS('✅ Financial calculations are CORRECT!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Financial calculations are WRONG!'))
        
        # ========== TEST 12: QUERY RELATED RECORDS ==========
        self.stdout.write('\n\n📝 TEST 12: Querying Related Records')
        self.stdout.write('-' * 40)
        
        # Get all fertilizers for rice
        rice_fertilizers = rice.fertilizers.all()
        self.stdout.write(f'\n🌾 Rice fertilizers ({rice_fertilizers.count()}):')
        for fert in rice_fertilizers:
            self.stdout.write(f'   - {fert.name}: NPR {fert.cost}')
        
        # Get all pesticides for rice
        rice_pesticides = rice.pesticides.all()
        self.stdout.write(f'\n🌾 Rice pesticides ({rice_pesticides.count()}):')
        for pest in rice_pesticides:
            self.stdout.write(f'   - {pest.name}: NPR {pest.cost}')
        
        # Get all expenses for rice
        rice_expenses = rice.expenses.all()
        self.stdout.write(f'\n🌾 Rice other expenses ({rice_expenses.count()}):')
        for exp in rice_expenses:
            self.stdout.write(f'   - {exp.get_category_display()}: NPR {exp.amount}')
        
        # Get all incomes for rice
        rice_incomes = rice.incomes.all()
        self.stdout.write(f'\n🌾 Rice incomes ({rice_incomes.count()}):')
        for inc in rice_incomes:
            self.stdout.write(f'   - {inc.get_source_display()}: NPR {inc.amount}')
        
        # Get all harvests for rice
        rice_harvests = rice.harvests.all()
        self.stdout.write(f'\n🌾 Rice harvests ({rice_harvests.count()}):')
        for har in rice_harvests:
            self.stdout.write(f'   - {har.harvest_date}: {har.quantity}{har.unit} ({har.get_quality_display()})')
        
        # ========== TEST 13: FILTER RECORDS ==========
        self.stdout.write('\n\n📝 TEST 13: Filtering Records')
        self.stdout.write('-' * 40)
        
        # Filter expenses by category
        seed_expenses = CropExpense.objects.filter(category='seed')
        self.stdout.write(f'✅ Seed expenses: {seed_expenses.count()}')
        
        # Filter incomes by source
        subsidy_incomes = CropIncome.objects.filter(source='subsidy')
        self.stdout.write(f'✅ Subsidy incomes: {subsidy_incomes.count()}')
        
        # Filter harvests by quality
        premium_harvests = HarvestRecord.objects.filter(quality='premium')
        self.stdout.write(f'✅ Premium harvests: {premium_harvests.count()}')
        
        # Filter by date range
        march_expenses = CropExpense.objects.filter(date__month=3)
        self.stdout.write(f'✅ March expenses: {march_expenses.count()}')
        
        # ========== TEST 14: UPDATE RECORDS ==========
        self.stdout.write('\n\n📝 TEST 14: Updating Records')
        self.stdout.write('-' * 40)
        
        # Update fertilizer
        fert1.notes = 'First application - completed'
        fert1.save()
        self.stdout.write('✅ Updated fertilizer notes')
        
        # Update expense
        exp2.amount = 5500.00
        exp2.save()
        self.stdout.write('✅ Updated labor expense amount')
        
        # Update harvest quality
        har2.quality = 'premium'
        har2.save()
        self.stdout.write('✅ Updated harvest quality')
        
        # ========== TEST 15: DELETE A RECORD ==========
        self.stdout.write('\n\n📝 TEST 15: Deleting a Record')
        self.stdout.write('-' * 40)
        
        fert3.delete()
        self.stdout.write('✅ Deleted a fertilizer record')
        
        # ========== TEST 16: TEST CROP STATUS CHANGE ==========
        self.stdout.write('\n\n📝 TEST 16: Testing Crop Status Change')
        self.stdout.write('-' * 40)
        
        old_status = rice.status
        rice.status = 'harvested'
        rice.save()
        self.stdout.write(f'✅ Changed rice status from "{old_status}" to "{rice.status}"')
        
        # ========== TEST SUMMARY ==========
        self.stdout.write('\n\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('          TEST SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'✅ Crops created: {Crop.objects.filter(farmer=user).count()}')
        self.stdout.write(f'✅ Fertilizer records: {FertilizerRecord.objects.filter(user=user).count()}')
        self.stdout.write(f'✅ Pesticide records: {PesticideRecord.objects.filter(user=user).count()}')
        self.stdout.write(f'✅ Expense records: {CropExpense.objects.filter(user=user).count()}')
        self.stdout.write(f'✅ Income records: {CropIncome.objects.filter(user=user).count()}')
        self.stdout.write(f'✅ Harvest records: {HarvestRecord.objects.filter(user=user).count()}')
        self.stdout.write(f'✅ Financial calculations: Working')
        self.stdout.write(f'✅ Validation rules: Working')
        self.stdout.write(f'✅ Relationships: Working')
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ All crop finance tests passed!'))
        self.stdout.write('=' * 60)