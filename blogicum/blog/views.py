from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Category
from .forms  import PostForm, CommentForm



POSTS_ON_PAGE: int = getattr(settings, 'POSTS_ON_INDEX', 10)


def index(request):
    post_list = (Post.objects
                 .filter(is_published=True, pub_date__lte=timezone.now())
                 .select_related('author', 'location', 'category')
                 .order_by('-pub_date'))
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = (category.posts
             .filter(is_published=True, pub_date__lte=timezone.now())
             .select_related('author', 'location')
             .order_by('-pub_date'))
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})
    

def profile(request, username):
    author = get_object_or_404(settings.AUTH_USER_MODEL, username=username)
    posts = (author.posts
             .filter(pub_date__lte=timezone.now())
             .select_related('category', 'location')
             .order_by('-pub_date'))
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html',
                  {'author': author, 'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author').order_by('created')
    form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})

class IndexView(ListView):
    model         = Post
    template_name = 'blog/index.html'
    ordering      = '-pub_date'
    paginate_by   = 10


class ProfilePostsView(ListView):
    model         = Post
    template_name = 'blog/profile.html'
    paginate_by   = 10
    def get_queryset(self):
        return Post.objects.filter(author__username=self.
                                   kwargs['username']).order_by('-pub_date')
    

class CategoryView(ListView):
    model         = Post
    template_name = 'blog/category.html'
    paginate_by   = 10
    def get_queryset(self):
        return Post.objects.filter(category__slug=self.
                                   kwargs['slug']).order_by('-pub_date')


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author

class PostCreateView(LoginRequiredMixin, CreateView):
    model         = Post
    form_class    = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:profile',
                            kwargs={'username': self.request.user.username})

class PostUpdateView(AuthorRequiredMixin, UpdateView):
    model         = Post
    form_class    = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(AuthorRequiredMixin, DeleteView):
    model         = Post
    template_name = 'blog/post_confirm_delete.html'
    def get_success_url(self):
        return reverse_lazy('users:profile', 
                            kwargs={'username': self.request.user.username})


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('users:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})

@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post   = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)

@login_required
def comment_edit(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment_edit.html', 
                  {'form': form, 'comment': comment})

@login_required
def comment_delete(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author == request.user:
        comment.delete()
    return redirect('blog:post_detail', pk=post_id)