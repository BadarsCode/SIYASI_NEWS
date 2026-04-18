"""
URL configuration for SIYASI_NEWS project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from News.admin import siyasi_admin_site

urlpatterns = [
    path('control-panel/', siyasi_admin_site.urls),
    path('', include('News.urls')),
]

if settings.DEBUG or getattr(settings, 'SERVE_MEDIA', False):
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    else:
        from django.urls import re_path
        from django.views.static import serve
        urlpatterns += [
            re_path(rf"^{settings.MEDIA_URL.lstrip('/')}(?P<path>.*)$", serve, {'document_root': settings.MEDIA_ROOT}),
        ]
