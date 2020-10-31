from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.urls import path, include
from .views import HomeView

# For sentry test
def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', HomeView.as_view(), name='home'),
    path('users/', include('users.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

