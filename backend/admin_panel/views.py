from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import csv
import uuid

import json
from openpyxl import Workbook

from django.contrib.auth import get_user_model
from crops.models import Crop, CropKnowledgeBase
from finance.serializers import TransactionSerializer
from livestock.models import Animal, AnimalType, BreedingRecord, HealthRecord, MilkRecord
from finance.models import Transaction
from .models import Notification, SystemSetting, AdminLog, Report
from .permissions import IsAdminUser
from .serializers import *
from .services import ReportGeneratorService

User = get_user_model()


# ============================================================
# AUTHENTICATION VIEWS
# ============================================================

class AdminLoginView(APIView):
    """Admin login endpoint"""
    permission_classes = []
    
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input', 'details': serializer.errors}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_admin and not user.is_superuser:
            return Response({'error': 'Unauthorized: Admin access only'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        refresh = RefreshToken.for_user(user)
        
        # Log admin login
        AdminLog.objects.create(
            admin_user=user,
            action='LOGIN',
            model_name='Auth',
            object_repr=user.username,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': AdminProfileSerializer(user).data
        })


class AdminProfileView(APIView):
    """Get admin profile"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        serializer = AdminProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = AdminProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminChangePasswordView(APIView):
    """Change admin password"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Current password is incorrect'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        AdminLog.objects.create(
            admin_user=user,
            action='UPDATE',
            model_name='User',
            object_repr=user.username,
            changes={'password_changed': True}
        )
        
        return Response({'message': 'Password changed successfully'})


class AdminLogoutView(APIView):
    """Admin logout"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            AdminLog.objects.create(
                admin_user=request.user,
                action='LOGOUT',
                model_name='Auth',
                object_repr=request.user.username
            )
        except Exception:
            pass
        
        return Response({'message': 'Logged out successfully'})


# ============================================================
# DASHBOARD VIEWS
# ============================================================

class DashboardStatsView(APIView):
    """Main dashboard statistics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Farmer statistics
        total_farmers = User.objects.filter(is_farmer=True).count()
        active_farmers = User.objects.filter(is_farmer=True, is_active=True).count()
        inactive_farmers = User.objects.filter(is_farmer=True, is_active=False).count()
        pending_farmers = User.objects.filter(is_farmer=True, is_email_verified=False).count()
        
        # Revenue statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        monthly_income = Transaction.objects.filter(
            transaction_type__contains='income',
            date__year=current_year,
            date__month=current_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_income = Transaction.objects.filter(
            transaction_type__contains='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Crop statistics
        total_crops = Crop.objects.count()
        active_crops = Crop.objects.filter(status='active').count()
        
        # Livestock statistics
        total_livestock = Animal.objects.count()
        active_livestock = Animal.objects.filter(status='active').count()
        
        # Pending approvals
        pending_approvals = User.objects.filter(is_farmer=True, is_active=False).count() + \
                           Crop.objects.filter(status='pending').count() if hasattr(Crop, 'pending') else 0
        
        return Response({
            'total_farmers': total_farmers,
            'active_farmers': active_farmers,
            'inactive_farmers': inactive_farmers,
            'pending_farmers': pending_farmers,
            'total_revenue_month': monthly_income,
            'total_revenue_all': total_income,
            'total_crops': total_crops,
            'active_crops': active_crops,
            'total_livestock': total_livestock,
            'active_livestock': active_livestock,
            'pending_approvals': pending_approvals
        })


class FarmerRegistrationTrendView(APIView):
    """Farmer registration trend for charts"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        months = 6
        trends = []
        
        for i in range(months - 1, -1, -1):
            date = timezone.now().date() - timedelta(days=30 * i)
            month_start = date.replace(day=1)
            if i > 0:
                month_end = (month_start + timedelta(days=32)).replace(day=1)
            else:
                month_end = timezone.now().date()
            
            count = User.objects.filter(
                is_farmer=True,
                date_joined__date__gte=month_start,
                date_joined__date__lt=month_end
            ).count()
            
            trends.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        return Response(trends)


class CropDistributionView(APIView):
    """Crop distribution by stage for pie chart"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        stages = ['seeding', 'vegetative', 'flowering', 'fruiting', 'harvest']
        distribution = []
        
        for stage in stages:
            count = Crop.objects.filter(growth_stage=stage).count()
            distribution.append({
                'name': stage.capitalize(),
                'value': count
            })
        
        return Response(distribution)


class RevenueTrendView(APIView):
    """Monthly revenue trend for bar chart"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        months = 6
        trends = []
        
        for i in range(months - 1, -1, -1):
            date = timezone.now().date() - timedelta(days=30 * i)
            month_start = date.replace(day=1)
            if i > 0:
                month_end = (month_start + timedelta(days=32)).replace(day=1)
            else:
                month_end = timezone.now().date()
            
            income = Transaction.objects.filter(
                transaction_type__contains='income',
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            expense = Transaction.objects.filter(
                transaction_type__contains='expense',
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            trends.append({
                'month': month_start.strftime('%b %Y'),
                'income': income,
                'expense': expense,
                'profit': income - expense
            })
        
        return Response(trends)


class TopCropsView(APIView):
    """Most popular crops"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        top_crops = Crop.objects.values('name').annotate(count=Count('id')).order_by('-count')[:5]
        return Response([
            {'name': item['name'], 'count': item['count']} for item in top_crops
        ])


class RecentActivitiesView(APIView):
    """Recent activities for dashboard"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        activities = []
        
        # Recent farmer registrations
        recent_farmers = User.objects.filter(is_farmer=True).order_by('-date_joined')[:5]
        for farmer in recent_farmers:
            activities.append({
                'id': f"farmer_{farmer.id}",
                'type': 'farmer_registration',
                'title': 'New Farmer Registered',
                'description': f'{farmer.get_full_name()} joined as a farmer',
                'timestamp': farmer.date_joined,
                'user_name': farmer.get_full_name(),
                'user_email': farmer.email
            })
        
        # Recent crop additions
        recent_crops = Crop.objects.order_by('-created_at')[:5]
        for crop in recent_crops:
            activities.append({
                'id': f"crop_{crop.id}",
                'type': 'crop_added',
                'title': 'New Crop Planted',
                'description': f'{crop.name} planted by {crop.farmer.get_full_name()}',
                'timestamp': crop.created_at,
                'user_name': crop.farmer.get_full_name(),
                'user_email': crop.farmer.email
            })
        
        # Recent transactions
        recent_transactions = Transaction.objects.order_by('-created_at')[:5]
        for trans in recent_transactions:
            trans_type = 'Income' if 'income' in trans.transaction_type else 'Expense'
            activities.append({
                'id': f"trans_{trans.id}",
                'type': 'transaction',
                'title': f'{trans_type} Recorded',
                'description': f'Rs. {trans.amount:,.2f} - {trans.description}',
                'timestamp': trans.created_at,
                'user_name': trans.user.get_full_name(),
                'user_email': trans.user.email
            })
        
        # Sort by timestamp and get latest 10
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return Response(activities[:10])


class AdminUserManagementView(APIView):
    """Manage admin users separately"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """List all admin users"""
        admins = User.objects.filter(is_admin=True).order_by('-date_joined')
        
        serializer = AdminUserListSerializer(admins, many=True)
        return Response({
            'admins': serializer.data,
            'count': admins.count()
        })
    
    def post(self, request):
        """Create a new admin user"""
        serializer = AdminUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            AdminLog.objects.create(
                admin_user=request.user,
                action='CREATE',
                model_name='Admin',
                object_id=str(user.id),
                object_repr=user.get_full_name(),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response(AdminUserListSerializer(user).data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, admin_id):
        """Remove admin (demote to regular user)"""
        try:
            admin_user = User.objects.get(id=admin_id, is_admin=True)
        except User.DoesNotExist:
            return Response({'error': 'Admin user not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Prevent deleting the last admin
        if User.objects.filter(is_admin=True).count() <= 1:
            return Response({'error': 'Cannot remove the last admin user'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        if admin_user.id == request.user.id:
            return Response({'error': 'You cannot remove your own admin account'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Demote to regular user (not farmer)
        admin_user.is_admin = False
        admin_user.is_farmer = False
        admin_user.save()
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='DELETE',
            model_name='Admin',
            object_id=str(admin_user.id),
            object_repr=admin_user.get_full_name(),
            changes={'demoted_to_user': True},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': f'{admin_user.get_full_name()} demoted to regular user'})

# ============================================================
# FARMER MANAGEMENT VIEWS
# ============================================================

class FarmerManagementView(APIView):
    """Complete farmer management - ONLY farmers (excludes admins)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # IMPORTANT: Only get users who are farmers AND NOT admins
        farmers = User.objects.filter(is_farmer=True, is_admin=False).order_by('-date_joined')
        
        # Search
        search = request.query_params.get('search')
        if search:
            farmers = farmers.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(farm_name__icontains=search)
            )
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter == 'active':
            farmers = farmers.filter(is_active=True, is_email_verified=True)
        elif status_filter == 'inactive':
            farmers = farmers.filter(is_active=False)
        elif status_filter == 'pending':
            farmers = farmers.filter(is_email_verified=False)
        
        # Filter by region
        region = request.query_params.get('region')
        if region:
            farmers = farmers.filter(geographical_region=region)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = farmers.count()
        farmers_page = farmers[start:end]
        
        return Response({
            'farmers': FarmerListSerializer(farmers_page, many=True).data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    def put(self, request, farmer_id):
        """Update farmer - can also promote to admin"""
        try:
            farmer = User.objects.get(id=farmer_id, is_farmer=True, is_admin=False)
        except User.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if promoting to admin
        if request.data.get('promote_to_admin'):
            if farmer.id == request.user.id:
                return Response({'error': 'You cannot promote yourself'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            farmer.is_admin = True
            farmer.is_farmer = False
            farmer.save()
            
            AdminLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Farmer',
                object_id=str(farmer.id),
                object_repr=farmer.get_full_name(),
                changes={'promoted_to_admin': True},
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response({
                'message': f'{farmer.get_full_name()} promoted to Admin',
                'user': {
                    'id': farmer.id,
                    'username': farmer.username,
                    'full_name': farmer.get_full_name(),
                    'is_admin': farmer.is_admin
                }
            })
        
        # Regular farmer update
        serializer = FarmerUpdateSerializer(farmer, data=request.data, partial=True)
        if serializer.is_valid():
            changes = serializer.validated_data
            serializer.save()
            
            AdminLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Farmer',
                object_id=str(farmer.id),
                object_repr=farmer.get_full_name(),
                changes=changes,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return Response(FarmerDetailSerializer(farmer).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, farmer_id):
        try:
            farmer = User.objects.get(id=farmer_id, is_farmer=True, is_admin=False)
        except User.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        farmer_name = farmer.get_full_name()
        farmer.delete()
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='DELETE',
            model_name='Farmer',
            object_id=str(farmer_id),
            object_repr=farmer_name,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Farmer deleted successfully'})


class FarmerBulkActionView(APIView):
    """Bulk actions on farmers"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = FarmerBulkActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        farmer_ids = serializer.validated_data['farmer_ids']
        action = serializer.validated_data['action']
        
        farmers = User.objects.filter(id__in=farmer_ids, is_farmer=True)
        count = farmers.count()
        
        if action == 'activate':
            farmers.update(is_active=True)
            message = f'{count} farmers activated'
        elif action == 'deactivate':
            farmers.update(is_active=False)
            message = f'{count} farmers deactivated'
        elif action == 'verify':
            farmers.update(is_email_verified=True)
            message = f'{count} farmers verified'
        elif action == 'delete':
            farmers.delete()
            message = f'{count} farmers deleted'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='BULK_ACTION',
            model_name='Farmer',
            changes={'action': action, 'count': count, 'ids': farmer_ids},
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': message, 'count': count})


class FarmerExportView(APIView):
    """Export farmers to CSV/Excel"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        format_type = request.query_params.get('format', 'csv')
        farmers = User.objects.filter(is_farmer=True)
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter == 'active':
            farmers = farmers.filter(is_active=True)
        elif status_filter == 'inactive':
            farmers = farmers.filter(is_active=False)
        
        if format_type == 'csv':
            return self.export_csv(farmers)
        elif format_type == 'excel':
            return self.export_excel(farmers)
        else:
            return Response({'error': 'Invalid format'}, status=status.HTTP_400_BAD_REQUEST)
    
    def export_csv(self, farmers):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="farmers_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Full Name', 'Email', 'Phone', 'Farm Name', 
                        'Region', 'Status', 'Join Date'])
        
        for farmer in farmers:
            writer.writerow([
                farmer.id, farmer.username, farmer.get_full_name(), farmer.email,
                farmer.phone or '-', farmer.farm_name or '-',
                farmer.get_geographical_region_display() or '-',
                'Active' if farmer.is_active else 'Inactive',
                farmer.date_joined.strftime('%Y-%m-%d')
            ])
        
        AdminLog.objects.create(
            admin_user=farmers.first().id if farmers.exists() else None,
            action='EXPORT',
            model_name='Farmer',
            changes={'format': 'csv', 'count': farmers.count()}
        )
        
        return response
    
    def export_excel(self, farmers):
        wb = Workbook()
        ws = wb.active
        ws.title = "Farmers Export"
        
        headers = ['ID', 'Username', 'Full Name', 'Email', 'Phone', 'Farm Name', 
                  'Region', 'Status', 'Join Date']
        ws.append(headers)
        
        for farmer in farmers:
            ws.append([
                farmer.id, farmer.username, farmer.get_full_name(), farmer.email,
                farmer.phone or '-', farmer.farm_name or '-',
                farmer.get_geographical_region_display() or '-',
                'Active' if farmer.is_active else 'Inactive',
                farmer.date_joined.strftime('%Y-%m-%d')
            ])
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="farmers_export.xlsx"'
        wb.save(response)
        
        return response


# ============================================================
# CROP MANAGEMENT VIEWS
# ============================================================

class CropManagementView(APIView):
    """Admin crop management"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, crop_id= None):
        if crop_id:
            return self.get_detail(request, crop_id )
        
        crops = Crop.objects.all().order_by('-created_at')
        
        # Search
        search = request.query_params.get('search')
        if search:
            crops = crops.filter(
                Q(name__icontains=search) |
                Q(farmer__username__icontains=search) |
                Q(farmer__first_name__icontains=search) |
                Q(farmer__last_name__icontains=search)
            )
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            crops = crops.filter(status=status_filter)
        
        # Filter by farmer
        farmer_id = request.query_params.get('farmer_id')
        if farmer_id:
            crops = crops.filter(farmer_id=farmer_id)


        district = request.query_params.get('district')
        if district:
            crops = crops.filter(
                Q(farmer__district__icontains=district) |
                Q(farmer__farm_district__icontains=district)
            )
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = crops.count()
        crops_page = crops[start:end]
        
        crops_data = CropListAdminSerializer(crops_page, many=True).data
        for i, crop in enumerate(crops_page):
            crops_data[i]['district'] = crop.farmer.district or crop.farmer.farm_district or 'N/A'
        
        return Response({
            'crops': CropListAdminSerializer(crops_page, many=True).data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    def get_detail(self, request, crop_id):
        try:

            try:
                # Try to parse as UUID
                crop_uuid = uuid.UUID(crop_id)
                crop = Crop.objects.get(id=crop_uuid)
            except (ValueError, TypeError):
                # If not UUID, try as integer
                crop = Crop.objects.get(id=int(crop_id))
        except Crop.DoesNotExist:
            return Response({'error': 'Crop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CropDetailAdminSerializer(crop)
        return Response(serializer.data)
    
    def delete(self, request, crop_id):
        try:
            crop = Crop.objects.get(id=crop_id)
        except Crop.DoesNotExist:
            return Response({'error': 'Crop not found'}, status=status.HTTP_404_NOT_FOUND)
        
        crop_name = crop.name
        crop.delete()
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='DELETE',
            model_name='Crop',
            object_id=str(crop_id),
            object_repr=crop_name,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Crop deleted successfully'})


class CropRegisterView(APIView):
    """Admin register crop for farmer"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = CropRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            farmer = User.objects.get(id=data['farmer_id'], is_farmer=True)
        except User.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            crop_template = CropKnowledgeBase.objects.get(id=data['crop_id'])
        except CropKnowledgeBase.DoesNotExist:
            return Response({'error': 'Crop template not found'}, status=status.HTTP_404_NOT_FOUND)
        
        crop = Crop.objects.create(
            farmer=farmer,
            name=crop_template.name_en,
            variety='',
            field_name='',
            field_area=data['area_planted'],
            area_unit=data['area_unit'],
            planting_date=data['planting_date'],
            expected_harvest_date=data.get('expected_harvest_date'),
            status='active'
        )
        
        # Create soil parameters if provided
        if data.get('soil_ph'):
            # You can create SoilParameter model if needed
            pass
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='CREATE',
            model_name='Crop',
            object_id=str(crop.id),
            object_repr=crop.name,
            changes=data,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'message': 'Crop registered successfully',
            'crop_id': crop.id
        }, status=status.HTTP_201_CREATED)


# ============================================================
# FINANCIAL MANAGEMENT VIEWS
# ============================================================

# admin_panel/views.py - Add this class

class FinanceDashboardView(APIView):
    """Complete financial dashboard for admin"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        from finance.models import Transaction
        from django.db.models import Sum, Q
        from datetime import date, timedelta
        from collections import defaultdict
        
        user = request.user
        today = date.today()
        
        # Get filter parameters
        year = int(request.query_params.get('year', today.year))
        month = request.query_params.get('month')
        
        # Base queryset
        transactions = Transaction.objects.all()
        
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
                date__year=prev_year,
                date__month=prev_month
            )
        else:
            transactions = transactions.filter(date__year=year)
            period_name = str(year)
            
            # Get previous year for trend
            prev_trans = Transaction.objects.filter(date__year=year - 1)
        
        # Calculate totals
        total_income = float(transactions.filter(transaction_type__contains='income').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        total_expense = float(transactions.filter(transaction_type__contains='expense').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        net_balance = total_income - total_expense
        
        # Calculate trends
        prev_income = float(prev_trans.filter(transaction_type__contains='income').aggregate(
            total=Sum('amount')).get('total') or 0)
        prev_expense = float(prev_trans.filter(transaction_type__contains='expense').aggregate(
            total=Sum('amount')).get('total') or 0)
        
        income_trend = ((total_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
        expense_trend = ((total_expense - prev_expense) / prev_expense * 100) if prev_expense > 0 else 0
        balance_trend = income_trend - expense_trend
        
        # Income breakdown by category
        incomes = transactions.filter(transaction_type__contains='income')
        income_dict = {}
        for inc in incomes:
            cat = inc.category or 'Other'
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
            cat = exp.category or 'Other'
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
        
        # Crop vs Livestock comparison
        crop_income = float(Transaction.objects.filter(
            transaction_type='crop_income'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        crop_expense = float(Transaction.objects.filter(
            transaction_type='crop_expense'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        livestock_income = float(Transaction.objects.filter(
            transaction_type='animal_income'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        livestock_expense = float(Transaction.objects.filter(
            transaction_type='animal_expense'
        ).aggregate(total=Sum('amount')).get('total') or 0)
        
        # Recent transactions
        recent_transactions = TransactionSerializer(
            transactions.order_by('-date')[:10], 
            many=True
        ).data
        
        data = {
            'period': period_name,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_balance': net_balance,
            'income_trend': round(income_trend, 1),
            'expense_trend': round(expense_trend, 1),
            'balance_trend': round(balance_trend, 1),
            'recent_transactions': recent_transactions,
            'income_breakdown': income_breakdown,
            'expense_breakdown': expense_breakdown,
            'monthly_trend': monthly_data,
            'crop_income': crop_income,
            'crop_expense': crop_expense,
            'livestock_income': livestock_income,
            'livestock_expense': livestock_expense,
        }
        
        return Response(data)

class TransactionManagementView(APIView):
    """View all transactions"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        transactions = Transaction.objects.all().order_by('-date')
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        # Filter by type
        trans_type = request.query_params.get('type')
        if trans_type:
            transactions = transactions.filter(transaction_type=trans_type)
        
        # Filter by farmer
        farmer_id = request.query_params.get('farmer_id')
        if farmer_id:
            transactions = transactions.filter(user_id=farmer_id)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = transactions.count()
        transactions_page = transactions[start:end]
        
        return Response({
            'transactions': TransactionAdminSerializer(transactions_page, many=True).data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        })


class RevenueByFarmerView(APIView):
    """Revenue breakdown by farmer"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        farmers = User.objects.filter(is_farmer=True)
        revenue_data = []
        
        for farmer in farmers:
            crops = Crop.objects.filter(farmer=farmer)
            total_income = sum(crop.total_income for crop in crops)
            total_expense = sum(crop.total_expense for crop in crops)
            
            if total_income > 0 or total_expense > 0:
                revenue_data.append({
                    'farmer_id': farmer.id,
                    'farmer_name': farmer.get_full_name(),
                    'total_income': total_income,
                    'total_expense': total_expense,
                    'net_profit': total_income - total_expense
                })
        
        # Sort by net profit
        revenue_data.sort(key=lambda x: x['net_profit'], reverse=True)
        
        return Response(revenue_data[:20])


# ============================================================
# LIVESTOCK MANAGEMENT VIEWS
# ============================================================

class LivestockManagementView(APIView):
    """Admin livestock management"""
    permission_classes = [IsAdminUser]
    
    def get(self, request, animal_id=None):
        """Handle both list and detail GET requests"""
        print(f"🔍 DEBUG: GET request received, animal_id={animal_id}")
        print(f"🔍 DEBUG: Query params: {request.query_params}")
        
        if animal_id:
            return self.get_detail(request, animal_id)
        return self.get_list(request)
    
    def get_list(self, request):
        """Get list of all animals"""
        print("🔍 DEBUG: Fetching livestock list")
        
        try:
            animals = Animal.objects.all().order_by('-created_at')
            print(f"🔍 DEBUG: Total animals found: {animals.count()}")
            
            # Filter by animal type
            animal_type = request.query_params.get('type')
            if animal_type:
                animals = animals.filter(animal_type__name__icontains=animal_type)
                print(f"🔍 DEBUG: After type filter: {animals.count()}")
            
            # Filter by status
            status_filter = request.query_params.get('status')
            if status_filter:
                animals = animals.filter(status=status_filter)
                print(f"🔍 DEBUG: After status filter: {animals.count()}")
            
            # Filter by gender
            gender = request.query_params.get('gender')
            if gender:
                animals = animals.filter(gender=gender)
                print(f"🔍 DEBUG: After gender filter: {animals.count()}")
            
            # Filter by farmer
            farmer_id = request.query_params.get('farmer_id')
            if farmer_id:
                animals = animals.filter(farmer_id=farmer_id)
                print(f"🔍 DEBUG: After farmer filter: {animals.count()}")
            
            # Search
            search = request.query_params.get('search')
            if search:
                animals = animals.filter(
                    Q(name__icontains=search) |
                    Q(tag_number__icontains=search) |
                    Q(farmer__username__icontains=search) |
                    Q(farmer__first_name__icontains=search) |
                    Q(farmer__last_name__icontains=search)
                )
                print(f"🔍 DEBUG: After search filter: {animals.count()}")
            
            # Pagination
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size
            
            total = animals.count()
            animals_page = animals[start:end]
            
            print(f"🔍 DEBUG: Serializing {animals_page.count()} animals")
            
            # Serialize the data
            serializer = LivestockListAdminSerializer(animals_page, many=True)
            
            response_data = {
                'livestock': serializer.data,
                'pagination': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
            
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ DEBUG: Error in get_list: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_detail(self, request, animal_id):
        """Get single animal detail"""
        try:
            import uuid
            try:
                animal_uuid = uuid.UUID(animal_id)
                animal = Animal.objects.get(id=animal_uuid)
            except (ValueError, TypeError):
                animal = Animal.objects.get(id=int(animal_id))
        except Animal.DoesNotExist:
            return Response({'error': 'Animal not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ DEBUG: Error finding animal: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            serializer = AdminLivestockDetailSerializer(animal)
            return Response(serializer.data)
        except Exception as e:
            print(f"❌ DEBUG: Error serializing animal: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, animal_id):
        """Delete an animal"""
        try:
            import uuid
            try:
                animal_uuid = uuid.UUID(animal_id)
                animal = Animal.objects.get(id=animal_uuid)
            except (ValueError, TypeError):
                animal = Animal.objects.get(id=int(animal_id))
        except Animal.DoesNotExist:
            return Response({'error': 'Animal not found'}, status=status.HTTP_404_NOT_FOUND)
        
        animal_name = animal.name or animal.tag_number
        animal.delete()
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='DELETE',
            model_name='Livestock',
            object_id=str(animal_id),
            object_repr=animal_name,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({'message': 'Animal deleted successfully'})    

class BreedingRecordsView(APIView):
    """View all breeding records"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Using your existing BreedingRecord model
        breeding_records = BreedingRecord.objects.all().order_by('-breeding_date')
        
        serializer = BreedingRecordAdminSerializer(breeding_records, many=True)
        return Response(serializer.data)


class MilkStatisticsView(APIView):
    """Milk production statistics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Last 30 days milk production
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        milk_records = MilkRecord.objects.filter(date__gte=start_date)
        
        daily_production = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            daily_total = milk_records.filter(date=date).aggregate(Sum('quantity_liters'))['quantity_liters__sum'] or 0
            daily_production.append({
                'date': date.strftime('%Y-%m-%d'),
                'total': daily_total
            })
        
        return Response({
            'daily_production': daily_production,
            'total_production': sum(d['total'] for d in daily_production),
            'average_per_day': sum(d['total'] for d in daily_production) / days if days > 0 else 0
        })


# ============================================================
# NOTIFICATION VIEWS
# ============================================================

class NotificationManagementView(APIView):
    """Send and manage notifications"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        notifications = Notification.objects.all().order_by('-sent_at')
        
        # Filter by type
        notif_type = request.query_params.get('type')
        if notif_type:
            notifications = notifications.filter(notification_type=notif_type)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = notifications.count()
        notifications_page = notifications[start:end]
        
        return Response({
            'notifications': NotificationSerializer(notifications_page, many=True).data,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
    
    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Create notification
        notification = Notification.objects.create(
            title=data['title'],
            message=data['message'],
            notification_type=data['notification_type'],
            priority=data.get('priority', 'medium'),
            sent_by=request.user
        )
        
        # Add target farmers if specified
        if data.get('target_farmers'):
            farmers = User.objects.filter(id__in=data['target_farmers'], is_farmer=True)
            notification.target_farmers.set(farmers)
        else:
            # Broadcast to all farmers
            all_farmers = User.objects.filter(is_farmer=True)
            notification.target_farmers.set(all_farmers)
        
        # Send email if requested
        if data.get('send_email'):
            self.send_email_notifications(notification)
        
        AdminLog.objects.create(
            admin_user=request.user,
            action='SEND_NOTIFICATION',
            model_name='Notification',
            object_id=str(notification.id),
            object_repr=notification.title,
            changes=data
        )
        
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
    
    def send_email_notifications(self, notification):
        """Send email notifications to farmers"""
        for farmer in notification.target_farmers.all():
            if farmer.email:
                send_mail(
                    subject=notification.title,
                    message=notification.message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[farmer.email],
                    fail_silently=True
                )


# ============================================================
# SYSTEM SETTINGS VIEWS
# ============================================================

class SystemSettingsView(APIView):
    """Manage system settings"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        setting_type = request.query_params.get('type')
        if setting_type:
            settings = SystemSetting.objects.filter(setting_type=setting_type, is_active=True)
        else:
            settings = SystemSetting.objects.filter(is_active=True)
        
        serializer = SystemSettingSerializer(settings, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SystemSettingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, setting_id):
        try:
            setting = SystemSetting.objects.get(id=setting_id)
        except SystemSetting.DoesNotExist:
            return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, setting_id):
        try:
            setting = SystemSetting.objects.get(id=setting_id)
        except SystemSetting.DoesNotExist:
            return Response({'error': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)
        
        setting.delete()
        return Response({'message': 'Setting deleted successfully'})


class CropCategoryManagementView(APIView):
    """Manage crop categories"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        categories = SystemSetting.objects.filter(setting_type='crop_category', is_active=True)
        serializer = CropCategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        data['setting_type'] = 'crop_category'
        serializer = SystemSettingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LivestockTypeManagementView(APIView):
    """Manage livestock types"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        types = SystemSetting.objects.filter(setting_type='livestock_type', is_active=True)
        serializer = LivestockTypeSerializer(types, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data
        data['setting_type'] = 'livestock_type'
        serializer = SystemSettingSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# REPORT VIEWS
# ============================================================

# admin_panel/views.py - Ensure ReportGenerationView returns the file correctly

class ReportGenerationView(APIView):
    """Generate and download reports"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = GenerateReportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        report_type = data['report_type']
        format_type = data['format']
        start_date = data['date_range_start']
        end_date = data['date_range_end']
        
        # Generate report using service (returns HttpResponse)
        response = ReportGeneratorService.generate_report(
            report_type=report_type,
            format=format_type,
            start_date=start_date,
            end_date=end_date,
            include_details=data.get('include_details', True),
            user=request.user
        )
        
        return response  


class ReportHistoryView(APIView):
    """View generated reports history"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        reports = Report.objects.all().order_by('-generated_at')
        
        # Filter by type
        report_type = request.query_params.get('type')
        if report_type:
            reports = reports.filter(report_type=report_type)
        
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    def delete(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        report.delete()
        return Response({'message': 'Report deleted successfully'})


# ============================================================
# ANALYTICS VIEWS
# ============================================================

class UserGrowthAnalyticsView(APIView):
    """User growth analytics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        period = request.query_params.get('period', 'monthly')
        
        if period == 'daily':
            days = 30
            data = self.get_daily_growth(days)
        elif period == 'weekly':
            weeks = 12
            data = self.get_weekly_growth(weeks)
        else:  # monthly
            months = 12
            data = self.get_monthly_growth(months)
        
        return Response(data)
    
    def get_daily_growth(self, days):
        data = []
        for i in range(days - 1, -1, -1):
            date = timezone.now().date() - timedelta(days=i)
            count = User.objects.filter(
                is_farmer=True,
                date_joined__date=date
            ).count()
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        return data
    
    def get_weekly_growth(self, weeks):
        data = []
        for i in range(weeks - 1, -1, -1):
            week_start = timezone.now().date() - timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            count = User.objects.filter(
                is_farmer=True,
                date_joined__date__gte=week_start,
                date_joined__date__lt=week_end
            ).count()
            data.append({
                'week': f"Week {week_start.strftime('%b %d')}",
                'count': count
            })
        return data
    
    def get_monthly_growth(self, months):
        data = []
        for i in range(months - 1, -1, -1):
            date = timezone.now().date() - timedelta(days=30 * i)
            month_start = date.replace(day=1)
            if i > 0:
                month_end = (month_start + timedelta(days=32)).replace(day=1)
            else:
                month_end = timezone.now().date()
            count = User.objects.filter(
                is_farmer=True,
                date_joined__date__gte=month_start,
                date_joined__date__lt=month_end
            ).count()
            data.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        return data


class GeographicDistributionView(APIView):
    """Geographic distribution of farmers"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Distribution by region
        region_distribution = User.objects.filter(
            is_farmer=True
        ).values('geographical_region').annotate(count=Count('id'))
        
        # Distribution by district
        district_distribution = User.objects.filter(
            is_farmer=True
        ).values('district').annotate(count=Count('id')).order_by('-count')[:10]
        
        return Response({
            'by_region': list(region_distribution),
            'by_district': list(district_distribution)
        })


class PlatformUsageAnalyticsView(APIView):
    """Platform usage analytics"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Most active farmers
        most_active_farmers = User.objects.filter(is_farmer=True).annotate(
            crop_count=Count('crops')
        ).order_by('-crop_count')[:10]
        
        # Most cultivated crops
        most_cultivated = Crop.objects.values('name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Popular livestock types
        popular_livestock = Animal.objects.values('animal_type__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'most_active_farmers': [
                {'id': f.id, 'name': f.get_full_name(), 'crop_count': f.crop_count}
                for f in most_active_farmers
            ],
            'most_cultivated_crops': list(most_cultivated),
            'popular_livestock': list(popular_livestock)
        })


class RevenueByRegionView(APIView):
    """Revenue breakdown by region"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        regions = ['terai', 'hilly', 'himalayan']
        region_revenue = []
        
        for region in regions:
            farmers = User.objects.filter(is_farmer=True, geographical_region=region)
            total_revenue = 0
            for farmer in farmers:
                crops = Crop.objects.filter(farmer=farmer)
                total_revenue += sum(crop.total_income for crop in crops)
            
            region_revenue.append({
                'region': region,
                'total_revenue': total_revenue,
                'farmer_count': farmers.count()
            })
        
        return Response(region_revenue)


# ============================================================
# ADMIN LOGS VIEW
# ============================================================

class AdminLogsView(APIView):
    """View admin action logs"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        logs = AdminLog.objects.all().order_by('-created_at')
        
        # Filter by admin
        admin_id = request.query_params.get('admin_id')
        if admin_id:
            logs = logs.filter(admin_user_id=admin_id)
        
        # Filter by action
        action = request.query_params.get('action')
        if action:
            logs = logs.filter(action=action)
        
        # Pagination
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = logs.count()
        logs_page = logs[start:end]
        
        return Response({
            'logs': [
                {
                    'id': log.id,
                    'admin': log.admin_user.username,
                    'action': log.action,
                    'model_name': log.model_name,
                    'object_repr': log.object_repr,
                    'changes': log.changes,
                    'ip_address': log.ip_address,
                    'created_at': log.created_at
                }
                for log in logs_page
            ],
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })