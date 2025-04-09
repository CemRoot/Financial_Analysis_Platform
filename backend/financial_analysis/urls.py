# backend/financial_analysis/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger API Dokümantasyonu
schema_view = get_schema_view(
   openapi.Info(
      title="Financial Analysis Platform API",
      default_version='v1',
      description="Financial Analysis Platform API Dokümantasyonu",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root URL redirects to React frontend
    path('', RedirectView.as_view(url='http://localhost:3000/'), name='frontend'),
    
    path('admin/', admin.site.urls),
    
    # JWT authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('api/stocks/', include('apps.stocks.urls')),
    path('api/news/', include('apps.news.urls')),
    path('api/predictions/', include('apps.predictions.urls')),  # Our new prediction endpoints

    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)