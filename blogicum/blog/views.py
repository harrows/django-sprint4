from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Post, Category

POSTS_PER_PAGE = 10


class PublishedMixin:
    """Фильтрует посты согласно условиям видимости."""
    queryset = Post.published.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.published()


class IndexView(PublishedMixin, ListView):
    template_name = "posts/index.html"
    paginate_by = POSTS_PER_PAGE


class ProfileView(PublishedMixin, ListView):
    template_name = "posts/profile.html"
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        user = get_object_or_404(
            self.model.objects.select_related("author"),
            author__username=self.kwargs["username"]
        ).author
        return super().get_queryset().filter(author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = get_object_or_404(
            self.model, author__username=self.kwargs["username"]
        ).author
        return context


class CategoryView(PublishedMixin, ListView):
    template_name = "posts/category.html"
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_published=True
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(DetailView):
    queryset = Post.published.all()
    template_name = "posts/detail.html"


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ("title", "text", "image", "category", "is_published")
    template_name = "posts/form.html"
    success_url = reverse_lazy("posts:index")

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        return super().form_valid(form)


class AuthorPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class PostUpdateView(AuthorPermissionMixin, LoginRequiredMixin, UpdateView):
    model = Post
    fields = ("title", "text", "image", "category", "is_published")
    template_name = "posts/form.html"

    def get_success_url(self):
        return reverse_lazy("posts:post_detail", kwargs={"pk": self.object.pk})


class PostDeleteView(AuthorPermissionMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/confirm_delete.html"
    success_url = reverse_lazy("posts:index")
