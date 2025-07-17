from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Category
from .forms import PostForm, CommentForm
from django.contrib.auth import get_user_model


# POSTS_PER_PAGE: int = getattr(settings, 'POSTS_ON_INDEX', 10)
POSTS_PER_PAGE = 10

def index(request):
    post_list = (Post.objects
                 .filter(is_published=True, pub_date__lte=timezone.now(),
                         category__is_published=True)
                 .select_related('author', 'location', 'category')
                 .order_by('-pub_date'))
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, is_published=True)
    posts = (category.posts
             .filter(is_published=True, pub_date__lte=timezone.now())
             .select_related('author', 'location')
             .order_by('-pub_date'))
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/category.html',
                  {'category': category, 'page_obj': page_obj})
    

def profile(request, username):
    User   = get_user_model()
    author = get_object_or_404(User, username=username)

    if request.user == author:
        posts = author.posts.all()
    else:
        posts = author.posts.filter(is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True)
    posts = posts.select_related('category', 'location').order_by('-pub_date')

    paginator  = Paginator(posts, POSTS_PER_PAGE)
    page_obj   = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/profile.html',
                  {'author': author, 'page_obj': page_obj})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('author').order_by('created')
    form = CommentForm()
    return render(request, 'blog/detail.html',
                  {'post': post, 'comments': comments, 'form': form})

class IndexView(ListView):
    template_name = 'blog/index.html'
    paginate_by   = POSTS_PER_PAGE

    def get_queryset(self):
        return (Post.objects
                .filter(is_published=True, pub_date__lte=timezone.now())
                .select_related('author', 'location', 'category')
                .order_by('-pub_date'))


class ProfilePostsView(ListView):
    template_name = 'blog/profile.html'
    paginate_by   = POSTS_PER_PAGE

    def get_queryset(self):
        self.profile_user = get_object_or_404(get_user_model(),
            username=self.kwargs['username'])
        
        posts_queryset = (Post.objects
                    .filter(author=self.profile_user)
                    .select_related('category', 'location')
                    .order_by('-pub_date'))
        if self.request.user != self.profile_user:
            posts_queryset = posts_queryset.filter(
                is_published=True,
                pub_date__lte=timezone.now(),
            )
        return posts_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        context['profile']      = self.profile_user
        return context
    

class CategoryView(ListView):
    template_name = 'blog/category.html'
    paginate_by   = POSTS_PER_PAGE

    def get_queryset(self):
        slug = self.kwargs['slug']
        return (Post.objects
                .filter(category__slug=slug,
                        category__is_published=True,
                        is_published=True,
                        pub_date__lte=timezone.now())
                .select_related('author', 'location', 'category')
                .order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['slug'], is_published=True
        )
        return context


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().author

class PostCreateView(LoginRequiredMixin, CreateView):
    model         = Post
    # form_class    = PostForm
    fields = ['title', 'text', 'image', 'category', 'location', 'pub_date']
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        # form.save()
        return super().form_valid(form)

    # def get_success_url(self):
    #     return reverse_lazy('users:profile',
    #                         kwargs={'username': self.request.user.username})
    def get_success_url(self):
        return reverse('profile', kwargs={'username': self.request.user.username})

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


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'blog/edit_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

class ProfileView(DetailView):
    model = User
    template_name = 'blog/user_profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        if self.request.user == user:
            posts = Post.objects.filter(author=user).order_by('-pub_date')
        else:
            posts = Post.objects.filter(author=user, pub_date__lte=timezone.now()).order_by('-pub_date')
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context

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
    post = get_object_or_404(Post, pk=post_id, is_published=True, pub_date__lte=timezone.now())
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
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

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    
    return render(request, 'blog/create.html', {'form': form, 'is_edit': True})