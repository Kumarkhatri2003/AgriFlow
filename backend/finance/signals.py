from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from datetime import timedelta
from crops.models import CropIncome, CropExpense
from livestock.models import AnimalIncome, AnimalExpense
from .models import Transaction, FinancialSummary


# ------------- CROP INCOME SIGNALS --------------------

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


# ------------------- CROP EXPENSE SIGNALS -----------------------

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


# -------------------- ANIMAL INCOME SIGNALS --------------------

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


# ------------------ ANIMAL EXPENSE SIGNALS -----------------------

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


# ------------------ UPDATE FINANCIAL SUMMARIES ------------------

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
        total=Sum('amount'))['amount__sum'] or 0
    daily_expense = daily_trans.filter(transaction_type__contains='expense').aggregate(
        total=Sum('amount'))['amount__sum'] or 0
    
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
        total=Sum('amount'))['amount__sum'] or 0
    month_expense = month_trans.filter(transaction_type__contains='expense').aggregate(
        total=Sum('amount'))['amount__sum'] or 0
    
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