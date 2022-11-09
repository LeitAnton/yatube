from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .models import Post, Group
from .forms import PostForm


User = get_user_model()


def pagination(request, posts, num):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


def index(request):
    posts = Post.objects.order_by('-pub_date').select_related('author')
    page, paginator = pagination(request, posts, 10)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).select_related('author').order_by('-pub_date')
    return render(request, 'group.html', {'group': group, 'posts': posts})


@login_required(redirect_field_name='login')
def new_post(request, post=None, title='Новая запись', button='Добавить'):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post', request.user, post.id)

        return render(request, 'new_post.html', {'form': form})

    form = PostForm(instance=post)
    return render(request, 'new_post.html', {'form': form, 'title': title, 'button': button})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).select_related('author').order_by('-pub_date')
    page, paginator = pagination(request, posts, 10)
    posts_count = len(posts)
    return render(request, 'profile.html', {'page': page, 'paginator': paginator, 'author': author, 'count': posts_count})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    posts_count = Post.objects.filter(author=author).count()
    return render(request, 'profile.html', {'author': author, 'post': post, 'count': posts_count})


@login_required(redirect_field_name='login')
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        post = get_object_or_404(Post, author=author, id=post_id)
        return new_post(request, post, 'Редактировать запись', 'Сохранить')
    else:
        return redirect('post', username, post_id)
