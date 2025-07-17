from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from .models import Post, Category, Comment
from django.db.models import Q

User = get_user_model()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class RulesPageView(TemplateView):
    template_name = 'pages/rules.html'


class ProfileView(ListView):
    model = Post
    template_name = 'profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        qs = Post.objects.filter(author=self.profile_user)
        if self.request.user != self.profile_user:
            qs = qs.filter(is_published=True, pub_date__lte=timezone.now())
        return qs.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'users/profile_edit.html'
    fields = ['first_name', 'last_name', 'email']

    def test_func(self):
        profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return self.request.user == profile_user

    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})


class IndexView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        qs = Post.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.filter(Q(is_published=True, pub_date__lte=timezone.now()) | Q(author=self.request.user))
        else:
            qs = qs.filter(is_published=True, pub_date__lte=timezone.now())
        return qs.order_by('-pub_date').distinct()


class CategoryView(ListView):
    model = Post
    template_name = 'category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        qs = Post.objects.filter(category=self.category)
        if self.request.user.is_authenticated:
            qs = qs.filter(Q(is_published=True, pub_date__lte=timezone.now()) | Q(author=self.request.user))
        else:
            qs = qs.filter(is_published=True, pub_date__lte=timezone.now())
        return qs.order_by('-pub_date').distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(post=self.object).order_by('created_at')
        context['form'] = CommentForm() if self.request.user.is_authenticated else None
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect(reverse('login') + '?next=' + request.path)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
        return redirect(reverse('post_detail', kwargs={'pk': self.object.pk}))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'posts/create_post.html'
    fields = ['title', 'text', 'image', 'category', 'pub_date', 'is_published']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/edit_post.html'
    fields = ['title', 'text', 'image', 'category', 'pub_date', 'is_published']

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.get_object().pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('index')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    template_name = 'comments/edit_comment.html'
    fields = ['text']

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def form_valid(self, form):
        self.object = form.save()

        return redirect(reverse('post_detail', kwargs={'pk': self.object.post.pk}))


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    pk_url_kwarg = "comment_id"
    
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        post_id = self.object.post.id
        if not self.object.post.is_published:
            return render(request, 'pages/404.html', status=404)
        self.object.delete()
        return redirect(reverse('post_detail', kwargs={'pk': post_id}))
