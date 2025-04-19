from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls'), name='documentation'),
    path('admin/', admin.site.urls, name='admin'),
    path('api/auth/', include('backend.ahs_auth.urls'), name='auth'),
    path('', include('backend.ahs_core.urls'), name='core'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += debug_toolbar_urls()
