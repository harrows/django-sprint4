from django.contrib.auth import (
    get_user_model,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, Q          # ← ❶ не забываем Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, EditProfileForm, PostForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE: int = 10           # при желании вынеси в settings

# ─────────────────────────── вспомогательные функции ────────────────────────────
def _get_posts_queryset(
    *,
    base_qs=Post.objects,
    filter_published: bool = True,
    select_related_fields: bool = True,
    annotate_comments: bool = True,
):
    qs = base_qs
    if filter_published:
        qs = qs.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
        ).filter(Q(category__is_published=True) | Q(category__isnull=True))

    if select_related_fields:
        qs = qs.select_related('author', 'location', 'category')

    if annotate_comments:
        qs = qs.annotate(comment_count=Count('comments'))

    return qs.order_by('-pub_date')

def _paginate(request, queryset, per_page: int = POSTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))

# ─────────────────────────────── главная страница ────────────────────────────────
def index(request):
    page_obj = _paginate(request, _get_posts_queryset())
    return render(request, 'blog/index.html', {'page_obj': page_obj})

# ─────────────────────────────── детальная страница ──────────────────────────────
def post_detail(request, post_id):
    """Автор видит черновики/отложки, другие — только опубликованное."""
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            _get_posts_queryset(select_related_fields=False), pk=post_id
        )

    comments = post.comments.select_related('author').order_by('created_at')
    return render(
        request,
        'blog/detail.html',
        {'post': post, 'form': CommentForm(), 'comments': comments},
    )

# ───────────────────────────────── категории ─────────────────────────────────────
def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = _get_posts_queryset(base_qs=category.posts)
    page_obj = _paginate(request, posts)
    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj,
    })

# ─────────────────────────────── профиль пользователя ────────────────────────────
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = _get_posts_queryset(
        base_qs=profile_user.posts,
        filter_published=request.user != profile_user,
    )
    page_obj = _paginate(request, posts)
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj,
        'posts': posts,          # нужен для <img> в шаблоне
    })

# ───────────────────────────── регистрация аккаунта ─────────────────────────────
def registration(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')                       # django.contrib.auth.urls
    return render(request, 'registration/registration_form.html', {'form': form})

# ─────────────────────────── редактирование профиля ─────────────────────────────
@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    form = EditProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})

@login_required
def change_password(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)        # чтобы не разлогинить
        return redirect('blog:profile', username=user.username)
    return render(request, 'registration/change_password.html', {'form': form})

# ──────────────────────────────── CRUD публикаций ───────────────────────────────
@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
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

# ────────────────────────────────── комментарии ─────────────────────────────────
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if request.method == 'POST' and form.is_valid():
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
