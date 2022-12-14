from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib.flatpages import views
from django.urls import path, include
from django.conf import settings
from django.contrib import admin

from .views import user_contact


urlpatterns = [
    path('', include("posts.urls")),
    path('contact/', user_contact, name='contact'),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include("users.urls")),
    path('auth/', include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='terms'),
]

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += (path('__debug__/', include('debug_toolbar.urls')),)
