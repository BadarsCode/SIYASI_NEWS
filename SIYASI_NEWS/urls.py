"""
URL configuration for SIYASI_NEWS project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from News.admin import siyasi_admin_site

urlpatterns = [
    path("control-panel/", siyasi_admin_site.urls),
    path("", include("News.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
