from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("core.urls")),
    path("", include("store.urls")),
    path("", include("orders.urls")),
    path("admin-panel/", include("dashboard.urls")),
    path("django-admin/", admin.site.urls),
]
from django.conf import settings
from django.conf.urls.static import static
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from orders.views import reset_admin_password

urlpatterns += [
    path("reset-admin-password/", reset_admin_password),
]
from orders.views import create_admin_user

urlpatterns += [
    path("create-admin-temp/", create_admin_user),
]
from orders.views import force_reset_password

urlpatterns += [
    path("force-reset/", force_reset_password),
]