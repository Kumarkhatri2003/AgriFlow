# finance/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from datetime import timedelta

# Import from crops app
from crops.models import (
    CropIncome, CropExpense, FertilizerRecord, 
    PesticideRecord, Labour
)

# Import from livestock app
from livestock.models import (
    AnimalIncome, AnimalExpense, VaccinationRecord, HealthRecord, Animal
)

from .models import Transaction, FinancialSummary


# ==================== CROP INCOME ====================
@receiver(post_save, sender=CropIncome)
def crop_income_to_transaction(sender, instance, created, **kwargs):
    """Create/update transaction when crop income is saved"""
    Transaction.objects.update_or_create(
        user=instance.user,
        source_id=str(instance.id),
        source_model='cropincome',
        defaults={
            'transaction_type': 'crop_income',
            'date': instance.date,
            'amount': instance.amount,
            'description': instance.description or f"{instance.get_source_display()}",
            'category': instance.get_source_display(),
            'crop': instance.crop,
        }
    )


@receiver(post_delete, sender=CropIncome)
def crop_income_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when crop income is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='cropincome'
    ).delete()


# ==================== CROP EXPENSE ====================
@receiver(post_save, sender=CropExpense)
def crop_expense_to_transaction(sender, instance, created, **kwargs):
    """Create/update transaction when crop expense is saved"""
    Transaction.objects.update_or_create(
        user=instance.user,
        source_id=str(instance.id),
        source_model='cropexpense',
        defaults={
            'transaction_type': 'crop_expense',
            'date': instance.date,
            'amount': instance.amount,
            'description': instance.description or f"{instance.get_category_display()}",
            'category': instance.get_category_display(),
            'crop': instance.crop,
        }
    )


@receiver(post_delete, sender=CropExpense)
def crop_expense_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when crop expense is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='cropexpense'
    ).delete()


# ==================== FERTILIZER RECORDS ====================
@receiver(post_save, sender=FertilizerRecord)
def fertilizer_to_transaction(sender, instance, created, **kwargs):
    """Create transaction when fertilizer expense is recorded"""
    if instance.cost > 0:  # Only create if there's a cost
        Transaction.objects.update_or_create(
            user=instance.user,
            source_id=str(instance.id),
            source_model='fertilizer',
            defaults={
                'transaction_type': 'crop_expense',
                'date': instance.application_date or instance.created_at.date(),
                'amount': instance.cost,
                'description': f"Fertilizer: {instance.name} ({instance.quantity}{instance.unit})",
                'category': f"Fertilizer",
                'crop': instance.crop,
            }
        )


@receiver(post_delete, sender=FertilizerRecord)
def fertilizer_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when fertilizer record is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='fertilizer'
    ).delete()


# ==================== PESTICIDE RECORDS ====================
@receiver(post_save, sender=PesticideRecord)
def pesticide_to_transaction(sender, instance, created, **kwargs):
    """Create transaction when pesticide expense is recorded"""
    if instance.cost > 0:  # Only create if there's a cost
        Transaction.objects.update_or_create(
            user=instance.user,
            source_id=str(instance.id),
            source_model='pesticide',
            defaults={
                'transaction_type': 'crop_expense',
                'date': instance.application_date or instance.created_at.date(),
                'amount': instance.cost,
                'description': f"Pesticide: {instance.name}",
                'category': "Pesticide",
                'crop': instance.crop,
            }
        )


@receiver(post_delete, sender=PesticideRecord)
def pesticide_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when pesticide record is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='pesticide'
    ).delete()


# ==================== LABOUR RECORDS ====================
@receiver(post_save, sender=Labour)
def labour_to_transaction(sender, instance, created, **kwargs):
    """Create transaction when labour expense is recorded"""
    if instance.total_cost > 0:  # Only create if there's a cost
        Transaction.objects.update_or_create(
            user=instance.user,
            source_id=str(instance.id),
            source_model='labour',
            defaults={
                'transaction_type': 'crop_expense',
                'date': instance.date or instance.created_at.date(),
                'amount': instance.total_cost,
                'description': f"Labour: {instance.name} ({instance.workers_count} workers × {instance.days} days)",
                'category': "Labour",
                'crop': instance.crop,
            }
        )


@receiver(post_delete, sender=Labour)
def labour_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when labour record is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='labour'
    ).delete()


# ==================== ANIMAL INCOME ====================
@receiver(post_save, sender=AnimalIncome)
def animal_income_to_transaction(sender, instance, created, **kwargs):
    """Create/update transaction when animal income is saved"""
    Transaction.objects.update_or_create(
        user=instance.user,
        source_id=str(instance.id),
        source_model='animalincome',
        defaults={
            'transaction_type': 'animal_income',
            'date': instance.date,
            'amount': instance.amount,
            'description': instance.description or f"{instance.get_source_display()}",
            'category': instance.get_source_display(),
            'animal': instance.animal,
        }
    )


@receiver(post_delete, sender=AnimalIncome)
def animal_income_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when animal income is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='animalincome'
    ).delete()


# ==================== ANIMAL ACQUISITION ====================
@receiver(post_save, sender=Animal)
def animal_acquisition_to_transactions(sender, instance, created, **kwargs):
    """Create transaction when an animal is purchased (has acquisition cost)"""
    if created and instance.acquisition_cost and instance.acquisition_cost > 0:
        Transaction.objects.update_or_create(
            user=instance.farmer,
            source_id=str(instance.id),
            source_model='animal_acquisition',
            defaults={
                'transaction_type': 'animal_expense',
                'date': instance.acquisition_date or instance.created_at.date(),  # Fixed: created_at.date()
                'amount': instance.acquisition_cost,
                'description': f"Animal Purchase: {instance.animal_type.name} - {instance.tag_number}",  # Fixed: animal_type
                'category': 'Animal Purchase',
                'animal': instance,
                'notes': f"Acquisition cost for {instance.animal_type.name} - {instance.tag_number}",
            }
        )
        
    elif not created and instance.acquisition_cost and instance.acquisition_cost > 0:
        transaction = Transaction.objects.filter(
            source_id=str(instance.id),
            source_model='animal_acquisition'
        ).first()
        
        if transaction:
            if transaction.amount != instance.acquisition_cost:
                transaction.amount = instance.acquisition_cost
                transaction.save()
        else:
            Transaction.objects.update_or_create(
                user=instance.farmer,
                source_id=str(instance.id),
                source_model='animal_acquisition',
                defaults={
                    'transaction_type': 'animal_expense',
                    'date': instance.acquisition_date or instance.created_at.date(),  # Fixed: created_at.date()
                    'amount': instance.acquisition_cost,
                    'description': f"Animal Purchase: {instance.animal_type.name} - {instance.tag_number}",  # Fixed: animal_type
                    'category': 'Animal Purchase',
                    'animal': instance,
                }
            )

@receiver(post_delete, sender=Animal)
def animal_acquisition_delete_transaction(sender,instance, **kwargs):
    """Delete transaction when animal is deleted"""
    Transaction.objects.filter(
        source_id = str(instance.id),
        source_model = 'animal_acquisition'        
    ).delete()
    


# ==================== ANIMAL EXPENSE ==================== 
@receiver(post_save, sender=AnimalExpense)
def animal_expense_to_transaction(sender, instance, created, **kwargs):
    """Create/update transaction when animal expense is saved"""
    Transaction.objects.update_or_create(
        user=instance.user,
        source_id=str(instance.id),
        source_model='animalexpense',
        defaults={
            'transaction_type': 'animal_expense',
            'date': instance.date,
            'amount': instance.amount,
            'description': instance.description or f"{instance.get_category_display()}",
            'category': instance.get_category_display(),
            'animal': instance.animal,
        }
    )


@receiver(post_delete, sender=AnimalExpense)
def animal_expense_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when animal expense is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='animalexpense'
    ).delete()


# ==================== VACCINATION RECORDS ====================
@receiver(post_save, sender=VaccinationRecord)
def vaccination_to_transaction(sender, instance, created, **kwargs):
    """Create transaction when vaccination expense is recorded"""
    if instance.cost > 0:  # Only create if there's a cost
        Transaction.objects.update_or_create(
            user=instance.animal.farmer,  # Get user from the animal
            source_id=str(instance.id),
            source_model='vaccination',
            defaults={
                'transaction_type': 'animal_expense',
                'date': instance.vaccine_date,
                'amount': instance.cost,
                'description': f"Vaccination: {instance.vaccine_name}",
                'category': "Vaccination",
                'animal': instance.animal,
            }
        )


@receiver(post_delete, sender=VaccinationRecord)
def vaccination_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when vaccination record is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='vaccination'
    ).delete()


# ==================== HEALTH RECORDS ====================
@receiver(post_save, sender=HealthRecord)
def healthrecord_to_transaction(sender, instance, created, **kwargs):
    """Create transaction when health record expense is recorded"""
    if instance.cost > 0:  # Only create if there's a cost
        Transaction.objects.update_or_create(
            user=instance.animal.farmer,  # Get user from the animal
            source_id=str(instance.id),
            source_model='healthrecord',
            defaults={
                'transaction_type': 'animal_expense',
                'date': instance.treatment_date,
                'amount': instance.cost,
                'description': f"Health: {instance.get_health_type_display()} - {instance.diagnosis[:50]}",
                'category': f"Health Care",
                'animal': instance.animal,
            }
        )


@receiver(post_delete, sender=HealthRecord)
def healthrecord_delete_transaction(sender, instance, **kwargs):
    """Delete transaction when health record is deleted"""
    Transaction.objects.filter(
        source_id=str(instance.id),
        source_model='healthrecord'
    ).delete()


# ==================== UPDATE FINANCIAL SUMMARIES ====================

def update_financial_summaries(user, transaction_date):
    """Update financial summaries for a user"""
    from datetime import date, timedelta
    
    today = transaction_date
    
    # Update daily summary
    daily_trans = Transaction.objects.filter(
        user=user,
        date=today
    )
    
    daily_income = daily_trans.filter(transaction_type__contains='income').aggregate(
        total=Sum('amount')).get('total') or 0
    daily_expense = daily_trans.filter(transaction_type__contains='expense').aggregate(
        total=Sum('amount')).get('total') or 0
    
    # Get previous day for trend
    yesterday = today - timedelta(days=1)
    yesterday_summary = FinancialSummary.objects.filter(
        user=user,
        period_type='daily',
        year=yesterday.year,
        month=yesterday.month,
        day=yesterday.day
    ).first()
    
    income_trend = 0
    expense_trend = 0
    if yesterday_summary:
        if yesterday_summary.total_income > 0:
            income_trend = ((daily_income - yesterday_summary.total_income) / yesterday_summary.total_income) * 100
        if yesterday_summary.total_expense > 0:
            expense_trend = ((daily_expense - yesterday_summary.total_expense) / yesterday_summary.total_expense) * 100
    
    # Income by category
    income_cats = {}
    for t in daily_trans.filter(transaction_type__contains='income'):
        cat = t.category
        income_cats[cat] = income_cats.get(cat, 0) + float(t.amount)
    
    # Expense by category
    expense_cats = {}
    for t in daily_trans.filter(transaction_type__contains='expense'):
        cat = t.category
        expense_cats[cat] = expense_cats.get(cat, 0) + float(t.amount)
    
    FinancialSummary.objects.update_or_create(
        user=user,
        period_type='daily',
        year=today.year,
        month=today.month,
        day=today.day,
        defaults={
            'total_income': daily_income,
            'total_expense': daily_expense,
            'net_balance': daily_income - daily_expense,
            'income_by_category': income_cats,
            'expense_by_category': expense_cats,
            'income_trend': round(income_trend, 1),
            'expense_trend': round(expense_trend, 1),
            'balance_trend': round(income_trend - expense_trend, 1),
        }
    )
    
    # Update monthly summary
    month_trans = Transaction.objects.filter(
        user=user,
        date__year=today.year,
        date__month=today.month
    )
    
    month_income = month_trans.filter(transaction_type__contains='income').aggregate(
        total=Sum('amount')).get('total') or 0
    month_expense = month_trans.filter(transaction_type__contains='expense').aggregate(
        total=Sum('amount')).get('total') or 0
    
    # Get previous month for trend
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year
    
    prev_month_summary = FinancialSummary.objects.filter(
        user=user,
        period_type='monthly',
        year=prev_year,
        month=prev_month
    ).first()
    
    month_income_trend = 0
    month_expense_trend = 0
    if prev_month_summary:
        if prev_month_summary.total_income > 0:
            month_income_trend = ((month_income - prev_month_summary.total_income) / prev_month_summary.total_income) * 100
        if prev_month_summary.total_expense > 0:
            month_expense_trend = ((month_expense - prev_month_summary.total_expense) / prev_month_summary.total_expense) * 100
    
    FinancialSummary.objects.update_or_create(
        user=user,
        period_type='monthly',
        year=today.year,
        month=today.month,
        defaults={
            'total_income': month_income,
            'total_expense': month_expense,
            'net_balance': month_income - month_expense,
            'income_trend': round(month_income_trend, 1),
            'expense_trend': round(month_expense_trend, 1),
            'balance_trend': round(month_income_trend - month_expense_trend, 1),
        }
    )


@receiver(post_save, sender=Transaction)
def update_summaries_on_transaction_save(sender, instance, **kwargs):
    """Update summaries when transaction is saved"""
    update_financial_summaries(instance.user, instance.date)


@receiver(post_delete, sender=Transaction)
def update_summaries_on_transaction_delete(sender, instance, **kwargs):
    """Update summaries when transaction is deleted"""
    update_financial_summaries(instance.user, instance.date)