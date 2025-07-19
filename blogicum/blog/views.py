from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = getattr(settings, 'POSTS_ON_INDEX', 10)


def registration(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/registration_form.html', {'form': form})


def _published_posts_queryset():
    return Post.objects.filter(
        Q(location__isnull=True) | Q(location__is_published=True),
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )


def _paginate(request, queryset):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    posts_list = (
        Post.objects.published()
        .annotate(comment_count=Count('comments'))
        .select_related('author', 'location', 'category')
        .order_by('-pub_date')
    )
    context = {'page_obj': paginate(request, posts_list)}
    return render(request, 'blog/index.html', context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts_list = (
        category.posts.published()
        .annotate(comment_count=Count('comments'))
        .select_related('author', 'location')
        .order_by('-pub_date')
    )
    context = {
        'category': category,
        'page_obj': paginate(request, posts_list),
    }
    return render(request, 'blog/category.html', context)



def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=post_id)
    if (not post.is_published or post.pub_date > timezone.now()) and post.author != request.user:
        return redirect('blog:index')

    comments = post.comments.select_related('author').order_by('created_at')
    return render(request, 'blog/detail.html', {'post': post, 'comments': comments})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = (
        author.posts.annotate(comment_count=Count('comments'))
        .select_related('location', 'category')
        .order_by('-pub_date')
    )
    context = {
        'author': author,
        'page_obj': paginate(request, posts_list),
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def change_password(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('blog:profile', username=user.username)
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/detail.html', {'post': post, 'form': form}, status=400)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})
