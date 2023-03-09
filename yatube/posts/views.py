from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def paginator(request: HttpRequest, posts):
    """This function takes an HTTP request and a list
    of posts as input and returns a paginated page
    object containing the posts."""
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return(page_obj)


def index(request: HttpRequest) -> HttpResponse:
    """This function takes an HTTP request as input and
    returns the ten most recent posts on the homepage."""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    page_obj = paginator(request, post_list)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """This function takes an HTTP request and a slug (a short label)
    as input and returns the ten most recent posts that belong
    to the specified group.."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(request, posts)
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """This function takes an HTTP request and a username as input
    and returns the user's profile page, along with all of their
    posts and the option to follow or unfollow them."""
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
    """This function takes an HTTP request and a post ID as input and
    returns a page containing the post's details, including
    the author, text, and comments."""
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
    """This function takes an HTTP request as input and
    creates a new post using the provided form data."""
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
    """This function takes an HTTP request and a post ID as input
    and allows the user to edit an existing post."""
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
    """This function takes an HTTP request and a post ID as input
    and allows the user to add a comment to the specified post."""
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
    """This function takes an HTTP request as input and returns a page
    containing all of the posts from the users
    the current user is following."""
    template = 'posts/follow.html'
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts_list)
    context = {'page_obj': page_obj, }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """This function takes an HTTP request and a username as input
    and allows the user to follow the specified user."""
    template = 'posts:profile'
    author = User.objects.get(username=username)
    exist_following = Follow.objects.filter(user=request.user,
                                            author=author).exists()
    if request.user.username != username and not exist_following:
        Follow.objects.create(user=request.user, author=author)
    return redirect(template, username=username)


@login_required
def profile_unfollow(request, username):
    """This function takes an HTTP request and a username as input
    and allows the user to unfollow the specified user."""
    author = User.objects.get(username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
