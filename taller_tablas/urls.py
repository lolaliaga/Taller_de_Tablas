from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from reparaciones.views import CustomLoginView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Login custom
    path("accounts/login/", CustomLoginView.as_view(), name="login"),

    # Logout + resto auth (logout, password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),

    # App principal
    path("", include("reparaciones.urls")),
]

# OJO: si usás esa condición con R2_PUBLIC_HOST, hacelo seguro:
if settings.DEBUG or not getattr(settings, "R2_PUBLIC_HOST", ""):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
