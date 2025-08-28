from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Додаємо маршрути для автентифікації
    path('users/', include('apps.users.urls')),

    path('', include('apps.personnel.urls')),
    path('staffing/', include('apps.staffing.urls')),
    path('reports/', include('apps.documents.urls')),
    path('reporting/', include('apps.reporting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass

admin.site.site_header = "АСООС 'ОБРІГ' - Адміністрування"
admin.site.site_title = "АСООС 'ОБРІГ'"
admin.site.index_title = "Панель управління"