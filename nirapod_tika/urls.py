from django.contrib import admin
from django.urls import path, include
import debug_toolbar  
from .views import api_root_view
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Nirapod Tika Vaccination Management System",
        default_version='v1',
        description="API Documentation for Nirapod Tika",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@nirapod-tika.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root_view),
    path('__debug__/', include(debug_toolbar.urls)),  
    path('api/v1/', include('api.urls')),
        path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)