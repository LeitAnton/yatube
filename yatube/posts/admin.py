from django.contrib import admin

from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "group", "text", "pub_date")
    search_fields = ("text",)
    list_filter = ("pub_date", "group")


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description")
    search_fields = ("title", "description")