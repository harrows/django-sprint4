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
    """Детальная страница поста с комментариями."""
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        post = get_object_or_404(
            _get_posts_queryset(select_related_fields=False),
            pk=post_id
        )

    comments = post.comments.select_related('author').order_by('created_at')
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, slug):
    """Страница постов определенной категории."""
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = _get_posts_queryset(base_qs=category.posts)
    page_obj = _paginate(request, posts)
    return render(request, 'blog/category.html', {'category': category, 'page_obj': page_obj})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = _get_posts_queryset(
        base_qs=profile_user.posts,
        filter_published=request.user != profile_user,
        show_future_to_author=request.user == profile_user
    )
    page_obj = _paginate(request, posts)
    return render(
        request,
        'blog/profile.html',
        {'profile': profile_user, 'page_obj': page_obj}
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

    user = get_object_or_404(User, username=username)
    form = EditProfileForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=username)
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
        post = get_object_or_404(Post, pk=post_id)
        if not post.is_published and post.author != request.user:
            raise Http404

        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post = post
                comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    except Post.DoesNotExist:
        raise Http404


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