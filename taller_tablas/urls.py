from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from reparaciones.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login/logout usando nuestra vista personalizada
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),

    # URLs de la app reparaciones
    path('', include('reparaciones.urls')),
]

if settings.DEBUG or not settings.R2_PUBLIC_HOST:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
