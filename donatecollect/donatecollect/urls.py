from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from collects.views import CollectViewSet
from payments.views import PaymentViewSet

router = DefaultRouter()
router.register(r'collects', CollectViewSet, basename='collect')
router.register(r'payments', PaymentViewSet, basename='payment')

schema_view = get_schema_view(
    openapi.Info(
        title="DonateCollect API",
        default_version='v1',
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)