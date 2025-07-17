from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Post, Category, Comment
from .forms import PostForm, ProfileEditForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUp(CreateView):
    form_class   = UserCreationForm
    template_name = 'registration/signup.html'
    success_url   = reverse_lazy('login')


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Последние обновления"
        return context


class CategoryView(ListView):
    model = Post
    template_name = 'blog/category_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.select_related('author', 'category').filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['title'] = f"Категория: {self.category.title}"
        return context


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.select_related('author', 'category').filter(author=self.profile_user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.profile_user
        context['title'] = f"Профиль пользователя: {self.profile_user.username}"
        return context


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('author').all()
    comment_form = None
    if request.method == 'POST':
        from .forms import CommentForm
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            return redirect('post_detail', pk=pk)
    else:
        try:
            from .forms import CommentForm
            comment_form = CommentForm()
        except ImportError:
            comment_form = None
    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        return redirect('profile', username=self.request.user.username)

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        return redirect('post_detail', pk=self.kwargs['pk'])

    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect('post_detail', pk=self.object.pk)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = reverse_lazy('index')

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return redirect('post_detail', pk=post.pk)

    def post(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != request.user and comment.post.author != request.user:
            return redirect('post_detail', pk=comment.post.pk)
        post_pk = comment.post.pk
        comment.delete()
        return redirect('post_detail', pk=post_pk)
