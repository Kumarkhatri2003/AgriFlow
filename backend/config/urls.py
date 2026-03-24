from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# ==================== SWAGGER CONFIGURATION ====================
schema_view = get_schema_view(
    openapi.Info(
        title="AgriFlow API",
        default_version='v1',
        description="Smart Agriculture Management System for Nepali Farmers",
        terms_of_service="https://www.agriflow.com/terms/",
        contact=openapi.Contact(email="support@agriflow.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/auth/', include('users.urls')),
    path('api/crops/', include('crops.urls')),
    path('api/livestock/', include('livestock.urls')),
    path('api/finance/', include('finance.urls')),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger.yaml/', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)