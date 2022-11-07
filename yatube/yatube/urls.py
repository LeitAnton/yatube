from django.contrib import admin
from django.urls import path, include

from .views import user_contact


urlpatterns = [
    path('', include("posts.urls")),
    path('contact/', user_contact, name='contact'),
    path('auth/', include("users.urls")),
    path('auth/', include("django.contrib.auth.urls")),
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
]
