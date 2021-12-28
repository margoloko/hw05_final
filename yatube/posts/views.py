from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def paginator(request: HttpRequest, posts):
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return(page_obj)


def index(request: HttpRequest) -> HttpResponse:
    """ Функция выводит на главную страницу десять последних постов."""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """ Функция group_posts передаёт в шаблон posts/group_list.html десять
    последних объектов модели Post, принадлежащих соответствующей группе."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """ Функция для отображения профиля пользователя."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    author_post = author.posts.filter(author=author)
    post_count = posts.count()
    page_obj = paginator(request, author_post)
    following = Follow.objects.filter(
        user=request.user and request.user.is_authenticated,
        author=author).exists()
    context = {'post_count': post_count,
               'author': author,
               'page_obj': page_obj,
               'following': following}
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """ Функция выводит детальную информацию о посте."""
    template = 'posts/post_detail.html'
    post_page = Post.objects.get(pk=post_id)
    post_count = Post.objects.filter(author=post_page.author).count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm()
    context = {'post_page': post_page,
               'post_count': post_count,
               'form': form,
               'comments': comments}
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """ Функция для создания поста."""
    template = 'posts/post_create.html'
    form = PostForm()
    context = {'form': form}
    if request.method == "POST":
        post_author = Post(author=request.user)
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post_author)
        if form.is_valid():
            form.cleaned_data['text']
            form.cleaned_data['group']
            form.save()
            return redirect('posts:profile', request.user)
        return render(request, template, {'form': form})
    return render(request, template, context)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """ Функция для редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    is_edit = True
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {'form': form,
               'is_edit': is_edit,
               'post_id': post_id,
               'post': post, }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """ Функция генерирует страницу с постами авторов,
    на которых подписан пользователь."""
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts_list)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """ Функция для подписки на авторов."""
    template = 'posts:profile'
    author = User.objects.get(username=username)
    exist_following = Follow.objects.filter(user=request.user,
                                            author=author).exists()
    if request.user.username != username and not exist_following:
        Follow.objects.create(user=request.user, author=author)
    return redirect(template, username=username)


@login_required
def profile_unfollow(request, username):
    """ Функция для редактирования поста."""
    author = User.objects.get(username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
