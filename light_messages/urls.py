"""
URL configuration for light_messages project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from .health import health_check


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    # Make sure to make ADMIN_URL a secret on production environments
    path(settings.ADMIN_URL, admin.site.urls),
    # Auth URLs
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Users URLs
    path("api/v1/users/", include("core_apps.users.urls")),
    # Conversations URLs
    path("api/v1/conversations/", include("core_apps.messenger.urls")),
    # Swagger | docs URLs
    path("api/v1/docs/", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Health Check URL
    path("api/v1/health/", health_check, name="health_check"),
]


### Optional Silk profiling URLs (only enabled if ENABLE_SILK is True in settings)
if getattr(settings, "ENABLE_SILK", False):
    urlpatterns += [
        path(
            f"{getattr(settings, 'SILK_URL_PREFIX', 'silk').strip('/')}/", include("silk.urls", namespace="silk")
        ),
    ]


### Add Media & Static URLs -- Now served by Nginx
# if settings.DEBUG:
#     from django.conf.urls.static import static
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)