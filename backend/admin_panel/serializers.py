from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import date, datetime, timedelta
from crops.models import Crop, CropKnowledgeBase
from livestock.models import Animal, AnimalType, BreedingRecord
from finance.models import Transaction
from .models import Notification, SystemSetting, AdminLog, Report

User = get_user_model()


# ==================== AUTHENTICATION SERIALIZERS ====================

class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AdminProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone', 'profile_picture', 'date_joined'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        return data


# ==================== FARMER MANAGEMENT SERIALIZERS ====================

class FarmerListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    farm_name = serializers.CharField(source='farm_name', default='-')
    region = serializers.CharField(source='get_geographical_region_display', default='-')
    status = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'phone', 
            'farm_name', 'region', 'date_joined', 'status'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_status(self, obj):
        if not obj.is_active:
            return 'Inactive'
        elif not obj.is_email_verified:
            return 'Pending'
        return 'Active'


class FarmerDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    region_display = serializers.CharField(source='get_geographical_region_display', read_only=True)
    farm_details = serializers.SerializerMethodField()
    crop_stats = serializers.SerializerMethodField()
    livestock_stats = serializers.SerializerMethodField()
    financial_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'phone', 'first_name', 'last_name',
            'date_of_birth', 'age', 'gender', 'geographical_region', 'region_display',
            'location', 'district', 'profile_picture', 'date_joined', 'is_active',
            'is_farmer', 'is_email_verified', 'farm_details', 'crop_stats', 
            'livestock_stats', 'financial_summary'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_age(self, obj):
        return obj.get_age()
    
    def get_farm_details(self, obj):
        return {
            'farm_name': obj.farm_name,
            'total_area': str(obj.total_farm_area) if obj.total_farm_area else None,
            'farm_district': obj.farm_district,
            'farm_municipality': obj.farm_municipality,
            'soil_type': obj.farm_soil_type,
            'water_source': obj.water_source,
            'has_complete_profile': obj.has_complete_farm_profile()
        }
    
    def get_crop_stats(self, obj):
        crops = Crop.objects.filter(farmer=obj)
        return {
            'total_crops': crops.count(),
            'active_crops': crops.filter(status='active').count(),
            'harvested_crops': crops.filter(status='harvested').count(),
            'recent_crops': [{'id': c.id, 'name': c.name, 'status': c.status} for c in crops[:5]]
        }
    
    def get_livestock_stats(self, obj):
        animals = Animal.objects.filter(farmer=obj)
        return {
            'total_animals': animals.count(),
            'active_animals': animals.filter(status='active').count(),
            'by_type': dict(animals.values('animal_type__name').annotate(count=Count('id')))
        }
    
    def get_financial_summary(self, obj):
        from django.db.models import Sum
        crops = Crop.objects.filter(farmer=obj)
        total_income = sum(crop.total_income for crop in crops)
        total_expense = sum(crop.total_expense for crop in crops)
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'net_profit': total_income - total_expense
        }


class FarmerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'location', 'district', 
                  'geographical_region', 'is_active', 'is_email_verified']


class FarmerBulkActionSerializer(serializers.Serializer):
    farmer_ids = serializers.ListField(child=serializers.IntegerField())
    action = serializers.ChoiceField(choices=['activate', 'deactivate', 'delete', 'verify'])


# ==================== CROP MANAGEMENT SERIALIZERS ====================

class CropListAdminSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    farmer_email = serializers.CharField(source='farmer.email', read_only=True)
    growth_stage_display = serializers.CharField(source='get_growth_stage_display', read_only=True)
    status_badge = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    class Meta:
        model = Crop
        fields = [
            'id', 'name', 'variety', 'farmer_name', 'farmer_email', 'field_name',
            'field_area', 'area_unit', 'planting_date', 'expected_harvest_date',
            'growth_stage', 'growth_stage_display', 'status', 'status_badge','district', 'created_at'
        ]
    
    def get_status_badge(self, obj):
        colors = {'active': 'green', 'harvested': 'blue', 'done': 'gray'}
        return {'text': obj.status, 'color': colors.get(obj.status, 'gray')}
    
    def get_district(self, obj):
        return obj.farmer.district or obj.farmer.farm_district or 'N/A'


class CropDetailAdminSerializer(serializers.ModelSerializer):
    farmer_info = serializers.SerializerMethodField()
    growth_timeline = serializers.SerializerMethodField()
    expense_breakdown = serializers.SerializerMethodField()
    harvest_details = serializers.SerializerMethodField()
    yield_analysis = serializers.SerializerMethodField()
    
    class Meta:
        model = Crop
        fields = '__all__'
    
    def get_farmer_info(self, obj):
        return {
            'id': obj.farmer.id,
            'name': obj.farmer.get_full_name(),
            'email': obj.farmer.email,
            'phone': obj.farmer.phone,
            'farm_name': obj.farmer.farm_name
        }
    
    def get_growth_timeline(self, obj):
        timeline = []
        # Updated stages to match your model
        stages = ['germination', 'vegetative', 'flowering', 'maturation', 'harvest']
        stage_display = {
            'germination': 'Germination',
            'vegetative': 'Vegetative',
            'flowering': 'Flowering',
            'maturation': 'Maturation',
            'harvest': 'Harvest'
        }
        
        current_stage = obj.growth_stage if obj.growth_stage else 'germination'
        
        for idx, stage in enumerate(stages):
            # Calculate estimated date for each stage (20 days per stage)
            estimated_days = idx * 20
            estimated_date = None
            if obj.planting_date:
                try:
                    estimated_date = obj.planting_date + timedelta(days=estimated_days)
                except:
                    estimated_date = None
            
            # Determine status
            stage_index = stages.index(stage)
            current_index = stages.index(current_stage) if current_stage in stages else 0
            
            if stage_index < current_index:
                status = 'completed'
            elif stage_index == current_index:
                status = 'current'
            else:
                status = 'upcoming'
            
            timeline.append({
                'stage': stage,
                'stage_display': stage_display.get(stage, stage.capitalize()),
                'status': status,
                'date': estimated_date
            })
        return timeline
    
    def get_expense_breakdown(self, obj):
        return {
            'fertilizers': float(obj.total_fertilizer_cost or 0),
            'pesticides': float(obj.total_pesticide_cost or 0),
            'labor': float(obj.total_labor_cost or 0),
            'other': float(obj.total_other_expense or 0),
            'total': float(obj.total_expense or 0)
        }
    
    def get_harvest_details(self, obj):
        harvests = obj.harvests.all()
        return {
            'count': harvests.count(),
            'total_quantity': sum(float(h.quantity) for h in harvests),
            'recent_harvests': [
                {
                    'date': h.harvest_date,
                    'quantity': float(h.quantity),
                    'quality': h.quality,
                    'unit': h.unit
                } 
                for h in harvests[:5]
            ]
        }
    
    def get_yield_analysis(self, obj):
        expected_yield = 1000  # Default value
        actual_yield = sum(float(h.quantity) for h in obj.harvests.all())
        achievement = (actual_yield / expected_yield * 100) if expected_yield > 0 else 0
        return {
            'expected_yield': expected_yield,
            'actual_yield': actual_yield,
            'achievement_percentage': round(achievement, 2)
        }

class CropRegisterSerializer(serializers.Serializer):
    farmer_id = serializers.IntegerField()
    crop_id = serializers.IntegerField()  # From CropKnowledgeBase
    planting_date = serializers.DateField()
    expected_harvest_date = serializers.DateField(required=False)
    area_planted = serializers.DecimalField(max_digits=10, decimal_places=2)
    area_unit = serializers.CharField()
    soil_ph = serializers.FloatField(required=False)
    soil_nitrogen = serializers.FloatField(required=False)
    soil_phosphorus = serializers.FloatField(required=False)
    soil_potassium = serializers.FloatField(required=False)


# ==================== FINANCIAL SERIALIZERS ====================

class TransactionAdminSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    farmer_email = serializers.CharField(source='user.email', read_only=True)
    formatted_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = '__all__'
    
    def get_formatted_amount(self, obj):
        prefix = '+' if 'income' in obj.transaction_type else '-'
        return f"{prefix} Rs. {obj.amount:,.2f}"


class RevenueByFarmerSerializer(serializers.Serializer):
    farmer_id = serializers.IntegerField()
    farmer_name = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=15, decimal_places=2)


# ==================== LIVESTOCK SERIALIZERS ====================

class LivestockListAdminSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    animal_type_name = serializers.CharField(source='animal_type.name', read_only=True)
    age_months = serializers.SerializerMethodField()
    is_pregnant = serializers.BooleanField(read_only=True)

    class Meta:
        model = Animal
        fields = [
            'id', 'name', 'tag_number', 'animal_type_name', 'gender',
            'age_months','status',
            'farmer_name', 'created_at','is_pregnant'
        ]
            
    def get_age_months(self,obj):
        """Calculate age in months from birth_date"""
        if obj.birth_date:
            today = date.today()
            months = (today.year-obj.birth_date.year)*12 + (today.month-obj.birth_date.month)
            
            return months
        return None
    
    
            
            
class BreedingRecordAdminSerializer(serializers.ModelSerializer):
    animal_name = serializers.CharField(source='animal.name', read_only=True)
    farmer_name = serializers.CharField(source='animal.farmer.get_full_name', read_only=True)
    
    class Meta:
        model = BreedingRecord
        fields = '__all__'


# ==================== NOTIFICATION SERIALIZERS ====================

class NotificationSerializer(serializers.ModelSerializer):
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['id', 'sent_by', 'sent_at']


class SendNotificationSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    message = serializers.CharField(max_length=None)
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    priority = serializers.ChoiceField(choices=Notification.PRIORITY_CHOICES, required=False)
    target_farmers = serializers.ListField(child=serializers.IntegerField(), required=False)
    send_email = serializers.BooleanField(default=False)


# ==================== SYSTEM SETTINGS SERIALIZERS ====================

class SystemSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = '__all__'


class CropCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = ['id', 'key', 'display_name', 'description', 'order', 'is_active']
        
class AdminLivestockDetailSerializer(serializers.ModelSerializer):
    """Detailed livestock serializer for admin"""
    farmer_name = serializers.CharField(source='farmer.get_full_name', read_only=True)
    farmer_email = serializers.CharField(source='farmer.email', read_only=True)
    animal_type_name = serializers.CharField(source='animal_type.name', read_only=True)
    
    class Meta:
        model = Animal
        fields = '__all__'


class LivestockTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSetting
        fields = ['id', 'key', 'display_name', 'description', 'order', 'is_active']


# ==================== REPORT SERIALIZERS ====================

class ReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'generated_by', 'generated_at', 'download_count']


class GenerateReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES)
    format = serializers.ChoiceField(choices=Report.FORMAT_CHOICES, default='csv')
    date_range_start = serializers.DateField()
    date_range_end = serializers.DateField()
    include_details = serializers.BooleanField(default=True)


# ==================== DASHBOARD STATS SERIALIZERS ====================

class DashboardStatsSerializer(serializers.Serializer):
    total_farmers = serializers.IntegerField()
    active_farmers = serializers.IntegerField()
    inactive_farmers = serializers.IntegerField()
    pending_farmers = serializers.IntegerField()
    
    total_revenue_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_revenue_all = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    total_crops = serializers.IntegerField()
    active_crops = serializers.IntegerField()
    
    total_livestock = serializers.IntegerField()
    active_livestock = serializers.IntegerField()
    
    pending_approvals = serializers.IntegerField()


class FarmerRegistrationTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    count = serializers.IntegerField()


class CropDistributionSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()


class RevenueTrendSerializer(serializers.Serializer):
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=15, decimal_places=2)
    expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit = serializers.DecimalField(max_digits=15, decimal_places=2)


class TopCropSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()


class RecentActivitySerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    timestamp = serializers.DateTimeField()
    user_name = serializers.CharField()
    user_email = serializers.CharField()
    
    
class AdminUserListSerializer(serializers.ModelSerializer):
    """List admin users"""
    full_name = serializers.SerializerMethodField()
    district = serializers.CharField( read_only=True, default='N/A')  # Add this line

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'district','date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Create admin user"""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            **validated_data,
            password=password,
            is_farmer=False,
            is_admin=True,
            is_email_verified=True
        )
        return user


class FarmerListSerializer(serializers.ModelSerializer):
    """List farmers (non-admin users)"""
    full_name = serializers.SerializerMethodField()
    farm_name = serializers.CharField( default='-')
    region = serializers.CharField( default='-')
    status = serializers.SerializerMethodField()
    district = serializers.CharField( read_only=True, default='N/A')  # Add this line
    geographical_region = serializers.CharField( read_only=True, default='')
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'email', 'phone', 
            'farm_name', 'region','district', 'geographical_region', 'date_joined', 'status'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_status(self, obj):
        if not obj.is_active:
            return 'Inactive'
        elif not obj.is_email_verified:
            return 'Pending'
        return 'Active'