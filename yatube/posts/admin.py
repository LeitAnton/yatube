from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "text", "pub_date")
    search_fields = ("text", )
    list_filter = ("pub_date", )