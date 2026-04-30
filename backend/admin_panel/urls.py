from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', views.AdminLoginView.as_view(), name='admin-login'),
    path('auth/profile/', views.AdminProfileView.as_view(), name='admin-profile'),
    path('auth/change-password/', views.AdminChangePasswordView.as_view(), name='admin-change-password'),
    path('auth/logout/', views.AdminLogoutView.as_view(), name='admin-logout'),
    
    # Dashboard
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/farmer-trend/', views.FarmerRegistrationTrendView.as_view(), name='farmer-trend'),
    path('dashboard/crop-distribution/', views.CropDistributionView.as_view(), name='crop-distribution'),
    path('dashboard/revenue-trend/', views.RevenueTrendView.as_view(), name='revenue-trend'),
    path('dashboard/top-crops/', views.TopCropsView.as_view(), name='top-crops'),
    path('dashboard/recent-activities/', views.RecentActivitiesView.as_view(), name='recent-activities'),
    
    # Farmer Management
    path('farmers/', views.FarmerManagementView.as_view(), name='farmers'),
    path('farmers/<int:farmer_id>/', views.FarmerManagementView.as_view(), name='farmer-detail'),
    path('farmers/bulk-action/', views.FarmerBulkActionView.as_view(), name='farmer-bulk-action'),
    path('farmers/export/', views.FarmerExportView.as_view(), name='farmer-export'),
    
    # Crop Management
    path('crops/', views.CropManagementView.as_view(), name='crops'),
    path('crops/<int:crop_id>/', views.CropManagementView.as_view(), name='crop-detail'),
    path('crops/register/', views.CropRegisterView.as_view(), name='crop-register'),
    
    # Financial Management
    path('finance/dashboard/', views.FinancialDashboardView.as_view(), name='finance-dashboard'),
    path('finance/transactions/', views.TransactionManagementView.as_view(), name='transactions'),
    path('finance/revenue-by-farmer/', views.RevenueByFarmerView.as_view(), name='revenue-by-farmer'),
    
    # Livestock Management
    path('livestock/', views.LivestockManagementView.as_view(), name='livestock'),
    path('livestock/<int:animal_id>/', views.LivestockManagementView.as_view(), name='livestock-detail'),
    path('livestock/breeding-records/', views.BreedingRecordsView.as_view(), name='breeding-records'),
    path('livestock/milk-stats/', views.MilkStatisticsView.as_view(), name='milk-stats'),
    
    # Notifications
    path('notifications/', views.NotificationManagementView.as_view(), name='notifications'),
    
    # System Settings
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    path('settings/crop-categories/', views.CropCategoryManagementView.as_view(), name='crop-categories'),
    path('settings/livestock-types/', views.LivestockTypeManagementView.as_view(), name='livestock-types'),
    path('settings/<int:setting_id>/', views.SystemSettingsView.as_view(), name='setting-detail'),
    
    # Reports
    path('reports/generate/', views.ReportGenerationView.as_view(), name='generate-report'),
    path('reports/history/', views.ReportHistoryView.as_view(), name='report-history'),
    path('reports/<int:report_id>/', views.ReportHistoryView.as_view(), name='report-delete'),
    
    # Analytics
    path('analytics/user-growth/', views.UserGrowthAnalyticsView.as_view(), name='user-growth'),
    path('analytics/geographic/', views.GeographicDistributionView.as_view(), name='geographic'),
    path('analytics/platform-usage/', views.PlatformUsageAnalyticsView.as_view(), name='platform-usage'),
    path('analytics/revenue-by-region/', views.RevenueByRegionView.as_view(), name='revenue-by-region'),
    
    # Admin Logs
    path('logs/', views.AdminLogsView.as_view(), name='admin-logs'),
]