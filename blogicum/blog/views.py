# blogicum/blog/views.py
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import Http404

from .forms import CommentForm, EditProfileForm, PostForm
from .models import Category, Comment, Post

from django.contrib.auth.forms import UserCreationForm

User = get_user_model()
POSTS_PER_PAGE: int = 10


def _get_posts_queryset(
    *,
    base_qs=Post.objects,
    filter_published: bool = True,
    select_related_fields: bool = True,
    annotate_comments: bool = True,
    show_future_to_author: bool = False
):
    qs = base_qs
    if filter_published:
        qs = qs.filter(
            is_published=True,
            category__is_published=True,
        )
        if not show_future_to_author:
            qs = qs.filter(pub_date__lte=timezone.now())

    if show_future_to_author:
        qs = qs | base_qs.filter(author=request.user, pub_date__gt=timezone.now())

    if select_related_fields:
        qs = qs.select_related('author', 'location', 'category')
    if annotate_comments:
        qs = qs.annotate(comment_count=Count('comments')).order_by(*Post._meta.ordering)
    return qs


def _paginate(request, queryset, per_page: int = POSTS_PER_PAGE):
    """Пагинация с сохранением аргумента page в строке запроса."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def index(request):
    """Главная страница со списком опубликованных постов."""
    page_obj = _paginate(request, _get_posts_queryset())
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    try:
        post = get_object_or_404(Post, pk=post_id)
    except Http404:
        return render(request, 'pages/404.html', status=404)

    # Разрешаем просмотр автору даже если пост не опубликован
    if not post.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)

    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)

    posts = category.posts.all()
    if request.user != category.author:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )

    posts = posts.select_related('author', 'location', 'category')
    posts = posts.annotate(comment_count=Count('comments')).order_by(*Post._meta.ordering)

    page_obj = _paginate(request, posts)
    return render(request, 'blog/category.html', {'category': category, 'page_obj': page_obj})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    is_owner = request.user == profile_user
    
    posts = profile_user.posts.all()
    if not is_owner:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
    posts = posts.select_related('author', 'location', 'category')
    posts = posts.annotate(comment_count=Count('comments')).order_by(*Post._meta.ordering)
    
    page_obj = _paginate(request, posts)
    return render(
        request,
        'blog/profile.html',
        {'profile': profile_user, 'page_obj': page_obj, 'is_owner': is_owner}
    )


def registration(request):
    """Регистрация нового пользователя."""
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'registration/registration_form.html', {'form': form})


@login_required
def edit_profile_self(request):
    """Редактирование своего профиля."""
    return edit_profile(request, request.user.username)


@login_required
def edit_profile(request, username):
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    user = request.user  # Используем текущего пользователя
    form = EditProfileForm(request.POST or None, instance=user)
    
    if form.is_valid():
        form.save()  # Просто сохраняем форму
        return redirect('blog:profile', username=user.username)
    
    return render(request, 'blog/user.html', {'form': form})


@login_required
def change_password(request, username):
    """Изменение пароля пользователя."""
    if request.user.username != username:
        return redirect('blog:profile', username=username)

    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('blog:profile', username=user.username)
    return render(request, 'registration/change_password.html', {'form': form})


@login_required
def change_password_self(request):
    """Изменение своего пароля."""
    return change_password(request, request.user.username)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        form.save_m2m()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})

@login_required
def post_edit(request, post_id):
    """Редактирование существующего поста."""
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
    """Удаление поста."""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/post_confirm_delete.html', {'post': post})


@login_required
def add_comment(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return render(request, 'pages/404.html', status=404)
    
    # Разрешаем комментарии только к опубликованным постам или постам автора
    if not post.is_published and post.author != request.user:
        return render(request, 'pages/404.html', status=404)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
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
    """Удаление комментария."""
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    return render(request, 'blog/comment_confirm_delete.html', {'comment': comment})