from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q
from datetime import date, timedelta
from collections import defaultdict
from decimal import Decimal
from .models import Transaction, FinancialSummary, Category, Budget
from .serializers import (
    TransactionSerializer, TransactionCreateSerializer, DashboardSerializer,
    FinancialSummarySerializer, CategorySerializer, BudgetSerializer
)


class DashboardView(APIView):
    """Get complete dashboard data with filters"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        today = date.today()
        
        # Get filter parameters
        year = int(request.query_params.get('year', today.year))
        month = request.query_params.get('month')
        
        # Base queryset
        transactions = Transaction.objects.filter(user=user)
        
        # Apply filters
        if month:
            transactions = transactions.filter(date__year=year, date__month=month)
            period_name = f"{year}-{int(month):02d}"
            
            # Get previous month for trend
            if int(month) == 1:
                prev_year = year - 1
                prev_month = 12
            else:
                prev_year = year
                prev_month = int(month) - 1
            
            prev_trans = Transaction.objects.filter(
                user=user,
                date__year=prev_year,
                date__month=prev_month
            )
        else:
            transactions = transactions.filter(date__year=year)
            period_name = str(year)
            
            # Get previous year for trend
            prev_trans = Transaction.objects.filter(
                user=user,
                date__year=year - 1
            )
        
        # Convert Decimal to float for all totals
        total_income = float(transactions.filter(transaction_type__contains='income').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        total_expense = float(transactions.filter(transaction_type__contains='expense').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        net_balance = total_income - total_expense
        
        prev_income = float(prev_trans.filter(transaction_type__contains='income').aggregate(
            total=Sum('amount')).get('total') or 0)
        prev_expense = float(prev_trans.filter(transaction_type__contains='expense').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        # Calculate trends
        income_trend = ((total_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
        expense_trend = ((total_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0
        
        # Recent transactions (last 10)
        recent = Transaction.objects.filter(user=user).order_by('-date')[:10]
        
        # Income breakdown by category
        incomes = transactions.filter(transaction_type__contains='income')
        income_dict = {}
        for inc in incomes:
            cat = inc.category
            amount = float(inc.amount)
            income_dict[cat] = income_dict.get(cat, 0) + amount
        
        income_breakdown = [
            {
                'category': k,
                'amount': v,
                'percentage': round((v / total_income * 100), 1) if total_income > 0 else 0
            }
            for k, v in sorted(income_dict.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Expense breakdown by category
        expenses = transactions.filter(transaction_type__contains='expense')
        expense_dict = {}
        for exp in expenses:
            cat = exp.category
            amount = float(exp.amount)
            expense_dict[cat] = expense_dict.get(cat, 0) + amount
        
        expense_breakdown = [
            {
                'category': k,
                'amount': v,
                'percentage': round((v / total_expense * 100), 1) if total_expense > 0 else 0
            }
            for k, v in sorted(expense_dict.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Monthly trend for the year
        monthly_data = []
        for m in range(1, 13):
            month_trans = Transaction.objects.filter(
                user=user,
                date__year=year,
                date__month=m
            )
            month_income = float(month_trans.filter(transaction_type__contains='income').aggregate(
                total=Sum('amount')).get('total') or 0)
            month_expense = float(month_trans.filter(transaction_type__contains='expense').aggregate(
                total=Sum('amount')).get('total') or 0)
            
            monthly_data.append({
                'month': m,
                'month_name': date(year, m, 1).strftime('%b'),
                'income': month_income,
                'expense': month_expense,
                'profit': month_income - month_expense,
            })
        
        # Comparison between Crops and Livestock
        crop_income = float(Transaction.objects.filter(
            user=user,
            transaction_type='crop_income'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        crop_expense = float(Transaction.objects.filter(
            user=user,
            transaction_type='crop_expense'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        livestock_income = float(Transaction.objects.filter(
            user=user,
            transaction_type='animal_income'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        livestock_expense = float(Transaction.objects.filter(
            user=user,
            transaction_type='animal_expense'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        general_income = float(Transaction.objects.filter(
            user=user,
            transaction_type__contains='income'
        ).exclude(transaction_type__in=['crop_income', 'animal_income']).aggregate(total=Sum('amount')).get('total') or 0)
        
        general_expense = float(Transaction.objects.filter(
            user=user,
            transaction_type__contains='expense'
        ).exclude(transaction_type__in=['crop_expense', 'animal_expense']).aggregate(total=Sum('amount')).get('total') or 0)
        
        data = {
            'period': period_name,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'income_trend': round(income_trend, 1),
            'expense_trend': round(expense_trend, 1),
            'balance_trend': round(income_trend - expense_trend, 1),
            'recent_transactions': TransactionSerializer(recent, many=True).data,
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
            'monthly_trend': monthly_data,
            'crop_income': crop_income,
            'crop_expense': crop_expense,
            'livestock_income': livestock_income,
            'livestock_expense': livestock_expense,
            'general_income': general_income,
            'general_expense': general_expense,
        }
        
        return Response(data)


class TransactionListView(generics.ListCreateAPIView):
    """List all transactions or create new"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter parameters
        source_model = self.request.query_params.get('source_model')  # fertilizer, pesticide, etc.

        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        t_type = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        # Date filters
        if year and month:
            queryset = queryset.filter(date__year=year, date__month=month)
        elif year:
            queryset = queryset.filter(date__year=year)
        elif start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        
        # Type filter
        if t_type and t_type.lower() == 'income':
            queryset = queryset.filter(transaction_type__contains='income')
        elif t_type and t_type.lower() == 'expense':
            queryset = queryset.filter(transaction_type__contains='expense')
        
        # Category filter
        if category:
            queryset = queryset.filter(category__icontains=category)
            
        #source filter
        if source_model:
            queryset = queryset.filter(source_model=source_model)
        
        # Search
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
        
        return queryset.order_by('-date')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a specific transaction"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class CategoryListView(generics.ListCreateAPIView):
    """List all categories or create new"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a category"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class BudgetListCreateView(generics.ListCreateAPIView):
    """List all budgets or create new"""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update or delete a budget"""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_update(self, serializer):
        budget = self.get_object()
        year = budget.year
        month = budget.month
        
        transactions = Transaction.objects.filter(
            user=self.request.user,
            date__year=year
        )
        if month:
            transactions = transactions.filter(date__month=month)
        
        actual_income = float(transactions.filter(transaction_type__contains='income').aggregate(
            total=Sum('amount')).get('total') or 0)
        actual_expense = float(transactions.filter(transaction_type__contains='expense').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        serializer.save(
            actual_income=actual_income,
            actual_expense=actual_expense
        )


class ReportExportView(APIView):
    """Export transactions to CSV"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        transactions = Transaction.objects.filter(user=user)
        if start_date and end_date:
            transactions = transactions.filter(date__range=[start_date, end_date])
        
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        filename = f"transactions_{start_date or 'all'}_{end_date or 'all'}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Category', 'Description', 'Amount', 'Crop/Animal'])
        
        for t in transactions.order_by('-date'):
            crop_animal = ''
            if t.crop:
                crop_animal = f"Crop: {t.crop.name}"
            elif t.animal:
                animal_name = t.animal.name or 'Unnamed'
                crop_animal = f"Animal: {animal_name} ({t.animal.tag_number})"
            
            writer.writerow([
                t.date,
                t.get_transaction_type_display(),
                t.category,
                t.description,
                f"{'+' if t.is_income else '-'}{t.amount}",
                crop_animal
            ])
        
        return response