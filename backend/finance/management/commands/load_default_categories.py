from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from finance.models import Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Load default categories for all users'

    def handle(self, *args, **options):
        # Default income categories
        income_categories = [
            ('crop_sale', 'Crop Sale', 'बाली बिक्री', 'crop'),
            ('subsidy', 'Government Subsidy', 'अनुदान', 'crop'),
            ('milk_sale', 'Milk Sale', 'दूध बिक्री', 'animal'),
            ('egg_sale', 'Egg Sale', 'अण्डा बिक्री', 'animal'),
            ('animal_sale', 'Animal Sale', 'पशु बिक्री', 'animal'),
            ('other_income', 'Other Income', 'अन्य आम्दानी', 'other'),
        ]
        
        # Default expense categories
        expense_categories = [
            ('seeds', 'Seeds', 'बीउ', 'crop'),
            ('fertilizer', 'Fertilizer', 'मल', 'crop'),
            ('pesticide', 'Pesticide', 'कीटनाशक', 'crop'),
            ('labor', 'Labor', 'ज्याला', 'crop'),
            ('land_rent', 'Land Rent', 'भाडा', 'crop'),
            ('irrigation', 'Irrigation', 'सिँचाइ', 'crop'),
            ('feed', 'Feed', 'दाना', 'animal'),
            ('medicine', 'Medicine', 'औषधि', 'animal'),
            ('vaccine', 'Vaccine', 'खोप', 'animal'),
            ('equipment', 'Equipment', 'उपकरण', 'animal'),
            ('transport', 'Transport', 'ढुवानी', 'other'),
            ('other_expense', 'Other Expense', 'अन्य खर्च', 'other'),
        ]
        
        users = User.objects.all()
        
        for user in users:
            count = 0
            # Create income categories
            for code, name, name_np, group in income_categories:
                cat, created = Category.objects.get_or_create(
                    user=user,
                    name=name,
                    category_type='income',
                    defaults={
                        'name_np': name_np,
                        'group': group,
                        'is_default': True
                    }
                )
                if created:
                    count += 1
            
            # Create expense categories
            for code, name, name_np, group in expense_categories:
                cat, created = Category.objects.get_or_create(
                    user=user,
                    name=name,
                    category_type='expense',
                    defaults={
                        'name_np': name_np,
                        'group': group,
                        'is_default': True
                    }
                )
                if created:
                    count += 1
            
            self.stdout.write(f"✅ Created {count} categories for {user.email}")
        
        self.stdout.write(self.style.SUCCESS('✅ Default categories loaded!'))