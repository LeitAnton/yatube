from django.urls import path

from .views import index, group_posts, new_post, profile, post_view, post_edit


urlpatterns = [
    path('', index, name="index"),
    path('new/', new_post, name='new_post'),
    path('group/<slug:slug>/', group_posts, name="group"),

    path('user/<str:username>/', profile, name='profile'),
    path('user/<str:username>/<int:post_id>/', post_view, name='post'),
    path('user/<str:username>/<int:post_id>/edit/', post_edit, name='post_edit'),
]