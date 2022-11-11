from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def pagination(request, posts, num):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page, paginator


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = list(Post.objects.order_by('-pub_date')
                 .select_related('author', 'group')
                 .prefetch_related('comments')
                 )
    page, paginator = pagination(request, posts, 10)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator,
                                          'title': 'Последние обновления на сайте',
                                          'index': True
                                          })


@cache_page(20, key_prefix='group_page')
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = list(Post.objects.filter(group=group)
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
    following = Follow.objects.filter(user=request.user, author=author)
    posts = list(Post.objects.filter(author=author)
                 .select_related('author', 'group')
                 .prefetch_related('comments')
                 .order_by('-pub_date')
                 )
    page, paginator = pagination(request, posts, 10)
    posts_count = len(posts)
    return render(request, 'profile.html', {'page': page,
                                            'paginator': paginator,
                                            'author': author,
                                            'count': posts_count,
                                            'following': following,
                                            })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    comments = list(Comment.objects.filter(post=post))
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


@cache_page(20, key_prefix='follow_page')
@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    posts = list(Post.objects.filter(author__following__in=follows)
                 .select_related('author', 'group')
                 .order_by('-pub_date')
                 .prefetch_related('comments')
                 )
    print(posts)
    page, paginator = pagination(request, posts, 10)
    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator,
                                          'title': 'Посты избранных авторов',
                                          })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        if not Follow.objects.filter(user=request.user, author=author):
            follow = Follow.objects.create(user=request.user, author=author)
            follow.save()
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        author = get_object_or_404(User, username=username)
        follow = get_object_or_404(Follow, user=request.user, author=author)
        follow.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
