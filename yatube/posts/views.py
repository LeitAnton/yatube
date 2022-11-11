from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .models import Post, Group, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def pagination(request, posts, num):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


def index(request):
    posts = list(Post.objects.order_by('-pub_date')
                 .select_related('author', 'group')
                 .prefetch_related('comments')
                 )
    page, paginator = pagination(request, posts, 10)
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = list(
                 Post.objects.filter(group=group)
                 .select_related('author', 'group')
                 .order_by('-pub_date')
                 .prefetch_related('comments')
                 )
    page, paginator = pagination(request, posts, 10)
    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required(redirect_field_name='login')
def new_post(request):
    title = 'Новая запись'
    button = 'Добавить'
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            user = request.user
            post.author = user
            post.save()
            return redirect('post', user, post.id)

        return render(request, 'new_post.html', {'form': form, 'title': title, 'button': button})

    form = PostForm()
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
    comments = Comment.objects.filter(post=post)
    posts_count = Post.objects.filter(author=author).count()
    return render(request, 'profile.html', {'author': author, 'post': post, 'count': posts_count, 'items': comments})


@login_required(redirect_field_name='login')
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        post = get_object_or_404(Post, author=author, id=post_id)
        if request.method == 'POST':
            form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('post', username, post.id)

            return render(request, 'new_post.html', {'form': form,
                                                     'title': 'Редактировать запись',
                                                     'button': 'Сохранить',
                                                     'username': username,
                                                     'post_id': post_id
                                                     })

        form = PostForm(instance=post)
        return render(request, 'new_post.html', {'form': form,
                                                 'title': 'Редактировать запись',
                                                 'button': 'Сохранить',
                                                 'username': username,
                                                 'post_id': post_id
                                                 })
    else:
        return redirect('post', username, post_id)


@login_required(redirect_field_name='login')
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post', author.username, post.id)

        return render(request, 'comments.html', {'form': form})

    form = CommentForm()
    return render(request, 'comments.html', {'form': form})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
