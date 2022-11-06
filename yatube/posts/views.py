from django.shortcuts import render, get_object_or_404

from .models import Post, Group


def index(request):
    latest = list(Post.objects.order_by("-pub_date").select_related("author"))
    return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related("author").order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})
