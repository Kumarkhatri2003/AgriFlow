from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, FinancialSummary, Category, Budget


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for Transaction model"""
    
    list_display = [
        'id', 'date', 'user', 'transaction_type_colored', 
        'category', 'amount_colored', 'description', 'linked_entity'
    ]
    list_filter = ['transaction_type', 'category', 'date', 'user']
    search_fields = ['description', 'category', 'user__username', 'user__email']
    date_hierarchy = 'date'
    readonly_fields = ['source_id', 'source_model', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'transaction_type', 'date', 'amount', 'description', 'category')
        }),
        ('Linked Entities', {
            'fields': ('crop', 'animal'),
            'classes': ('wide',),
            'description': 'Optional: Link this transaction to a specific crop or animal'
        }),
        ('Source Tracking', {
            'fields': ('source_id', 'source_model'),
            'classes': ('collapse',),
            'description': 'Auto-populated when transaction comes from crops/livestock'
        }),
        ('Additional Info', {
            'fields': ('notes', 'created_at'),
        }),
    )
    
    def amount_colored(self, obj):
        """Display amount with color (green for income, red for expense)"""
        if obj.is_income:
            return format_html(
                '{}',
                f'<span style="color: green; font-weight: bold;">+ NPR {obj.amount}</span>'
            )
        else:
            return format_html(
                '{}',
                f'<span style="color: red; font-weight: bold;">- NPR {obj.amount}</span>'
            )
    amount_colored.short_description = 'Amount'
    amount_colored.admin_order_field = 'amount'
    
    def transaction_type_colored(self, obj):
        """Display transaction type with emoji"""
        type_display = obj.get_transaction_type_display()
        emoji = {
            'crop_income': '🌾',
            'crop_expense': '🌾',
            'animal_income': '🐄',
            'animal_expense': '🐄',
        }.get(obj.transaction_type, '💰')
        
        return format_html('{} {}', emoji, type_display)
    transaction_type_colored.short_description = 'Type'
    transaction_type_colored.admin_order_field = 'transaction_type'
    
    def linked_entity(self, obj):
        """Show linked crop or animal if any"""
        if obj.crop:
            return format_html(
                '<a href="/admin/crops/crop/{}/change/">🌾 {}</a>',
                obj.crop.id, obj.crop.name
            )
        elif obj.animal:
            return format_html(
                '<a href="/admin/livestock/animal/{}/change/">🐄 {}</a>',
                obj.animal.id, obj.animal.name or obj.animal.tag_number
            )
        return '-'
    linked_entity.short_description = 'Linked To'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'crop', 'animal')


@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    """Admin for FinancialSummary model"""
    
    list_display = [
        'user', 'period_type', 'year', 'month', 'day',
        'total_income', 'total_expense', 'net_balance_display'
    ]
    list_filter = ['period_type', 'year', 'month', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Period Information', {
            'fields': ('user', 'period_type', 'year', 'month', 'day')
        }),
        ('Financial Totals', {
            'fields': ('total_income', 'total_expense', 'net_balance'),
            'classes': ('wide',)
        }),
        ('Trends', {
            'fields': ('income_trend', 'expense_trend', 'balance_trend'),
            'description': 'Percentage change from previous period'
        }),
        ('Breakdowns', {
            'fields': ('income_by_category', 'expense_by_category'),
            'classes': ('collapse',),
            'description': 'JSON data for charts'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def net_balance_display(self, obj):
        """Display net balance with color"""
        if obj.net_balance >= 0:
            return format_html(
                '{}',
                f'<span style="color: green; font-weight: bold;">+ NPR {obj.net_balance}</span>'
            )
        else:
            return format_html(
                '{}',
                f'<span style="color: red; font-weight: bold;">- NPR {abs(obj.net_balance)}</span>'
            )
    net_balance_display.short_description = 'Net Balance'
    net_balance_display.admin_order_field = 'net_balance'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    
    list_display = [
        'name', 'name_np', 'category_type_colored', 
        'group', 'user', 'is_default', 'is_active'
    ]
    list_filter = ['category_type', 'group', 'is_default', 'is_active', 'user']
    search_fields = ['name', 'name_np', 'user__username']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('user', 'name', 'name_np', 'category_type')
        }),
        ('Classification', {
            'fields': ('group', 'is_default', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def category_type_colored(self, obj):
        """Display category type with color"""
        if obj.category_type == 'income':
            return format_html('{}', '<span style="color: green;">💰 Income</span>')
        else:
            return format_html('{}', '<span style="color: red;">💸 Expense</span>')
    category_type_colored.short_description = 'Type'
    category_type_colored.admin_order_field = 'category_type'
    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} categories activated.")
    make_active.short_description = "Mark selected as active"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} categories deactivated.")
    make_inactive.short_description = "Mark selected as inactive"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    """Admin for Budget model"""
    
    list_display = [
        'user', 'year', 'month_display', 
        'planned_vs_actual_income', 'planned_vs_actual_expense',
        'progress_bars', 'status_indicator'
    ]
    list_filter = ['year', 'month', 'user']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['actual_income', 'actual_expense', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Budget Information', {
            'fields': ('user', 'year', 'month')
        }),
        ('Planned Amounts', {
            'fields': ('planned_income', 'planned_expense'),
            'classes': ('wide',)
        }),
        ('Actual Amounts (Auto-calculated)', {
            'fields': ('actual_income', 'actual_expense'),
            'classes': ('wide',)
        }),
        ('Category-wise Budgets', {
            'fields': ('category_budgets',),
            'classes': ('collapse',),
            'description': 'JSON data for category-specific budgets'
        }),
        ('Alert Settings', {
            'fields': ('alert_threshold',),
            'help_text': 'Alert when expense reaches this percentage of budget'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def month_display(self, obj):
        """Display month name or 'Yearly'"""
        if obj.month:
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return month_names[obj.month - 1]
        return 'Yearly'
    month_display.short_description = 'Month'
    month_display.admin_order_field = 'month'
    
    def planned_vs_actual_income(self, obj):
        """Show planned vs actual income"""
        planned = obj.planned_income
        actual = obj.actual_income
        diff = actual - planned
        
        if diff > 0:
            return format_html(
                '{}',
                f'P: NPR {planned}<br/>A: NPR {actual}<br/><span style="color: green;">+ NPR {diff}</span>'
            )
        elif diff < 0:
            return format_html(
                '{}',
                f'P: NPR {planned}<br/>A: NPR {actual}<br/><span style="color: orange;">- NPR {abs(diff)}</span>'
            )
        return format_html(
            '{}',
            f'P: NPR {planned}<br/>A: NPR {actual}'
        )
    planned_vs_actual_income.short_description = 'Income (Planned/Actual)'
    
    def planned_vs_actual_expense(self, obj):
        """Show planned vs actual expense"""
        planned = obj.planned_expense
        actual = obj.actual_expense
        diff = actual - planned
        
        if diff > 0:
            return format_html(
                '{}',
                f'P: NPR {planned}<br/>A: NPR {actual}<br/><span style="color: red;">+ NPR {diff}</span>'
            )
        elif diff < 0:
            return format_html(
                '{}',
                f'P: NPR {planned}<br/>A: NPR {actual}<br/><span style="color: green;">- NPR {abs(diff)}</span>'
            )
        return format_html(
            '{}',
            f'P: NPR {planned}<br/>A: NPR {actual}'
        )
    planned_vs_actual_expense.short_description = 'Expense (Planned/Actual)'
    
    def progress_bars(self, obj):
        """Show progress bars for income and expense"""
        income_progress = min(obj.progress_income, 100)
        expense_progress = min(obj.progress_expense, 100)
        
        income_color = '#22c55e'  # green
        expense_color = '#22c55e' if expense_progress <= 100 else '#ef4444'  # green or red
        
        return format_html(
            '''
            <div style="margin-bottom: 5px;">
                <div style="font-size: 11px;">Income: {:.1f}%</div>
                <div style="background-color: #e5e7eb; height: 8px; width: 150px; border-radius: 4px;">
                    <div style="background-color: {}; height: 8px; width: {}%; border-radius: 4px;"></div>
                </div>
            </div>
            <div>
                <div style="font-size: 11px;">Expense: {:.1f}%</div>
                <div style="background-color: #e5e7eb; height: 8px; width: 150px; border-radius: 4px;">
                    <div style="background-color: {}; height: 8px; width: {}%; border-radius: 4px;"></div>
                </div>
            </div>
            ''',
            income_progress, income_color, income_progress,
            expense_progress, expense_color, expense_progress
        )
    progress_bars.short_description = 'Progress'
    
    def status_indicator(self, obj):
        """Show status with emoji and color"""
        if obj.is_over_budget:
            return format_html('{}', '<span style="color: red; font-weight: bold;">⚠️ Over Budget</span>')
        elif obj.progress_expense >= obj.alert_threshold:
            return format_html('{}', '<span style="color: orange; font-weight: bold;">⚠️ Near Limit</span>')
        else:
            return format_html('{}', '<span style="color: green; font-weight: bold;">✅ On Track</span>')
    status_indicator.short_description = 'Status'
    
    actions = ['duplicate_budget', 'set_80_alert', 'set_90_alert']
    
    def duplicate_budget(self, request, queryset):
        """Duplicate selected budgets for next year/month"""
        count = 0
        for budget in queryset:
            # Check if budget already exists for next year
            exists = Budget.objects.filter(
                user=budget.user,
                year=budget.year + 1,
                month=budget.month
            ).exists()
            
            if not exists:
                Budget.objects.create(
                    user=budget.user,
                    year=budget.year + 1,
                    month=budget.month,
                    planned_income=budget.planned_income,
                    planned_expense=budget.planned_expense,
                    category_budgets=budget.category_budgets,
                    alert_threshold=budget.alert_threshold
                )
                count += 1
        
        self.message_user(request, f"Successfully duplicated {count} budget(s) for next year.")
    duplicate_budget.short_description = "Duplicate selected for next year"
    
    def set_80_alert(self, request, queryset):
        updated = queryset.update(alert_threshold=80)
        self.message_user(request, f"Alert threshold set to 80% for {updated} budget(s).")
    set_80_alert.short_description = "Set alert threshold to 80%"
    
    def set_90_alert(self, request, queryset):
        updated = queryset.update(alert_threshold=90)
        self.message_user(request, f"Alert threshold set to 90% for {updated} budget(s).")
    set_90_alert.short_description = "Set alert threshold to 90%"