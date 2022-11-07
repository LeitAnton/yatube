from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group
from .forms import PostForm


def index(request):
    latest = list(Post.objects.order_by('-pub_date').select_related('author'))
    return render(request, 'index.html', {'posts': latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author').order_by('-pub_date')[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})


@login_required(redirect_field_name='login')
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        form.author_id = request.user.id

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            return redirect('index')

        return render(request, 'new_post.html', {'form': form})

    form = PostForm
    return render(request, 'new_post.html', {'form': form})


