from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ---------------------------------------------
# Главный файл маршрутов проекта nikepro
# Подключает админку и приложение abibas
# ---------------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('abibas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
