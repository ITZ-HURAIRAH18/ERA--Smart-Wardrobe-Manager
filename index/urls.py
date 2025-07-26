from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login1.html'), name='login1'),

    path('jet', include('jet.urls','jet')),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
