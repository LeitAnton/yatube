from django.urls import path

from .views import index, group_posts, new_post


urlpatterns = [
    path('', index, name="index"),
    path('new/', new_post, name='new_post'),
    path('group/<slug:slug>/', group_posts, name="group"),
]