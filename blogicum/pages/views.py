from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView

from blog.models import Post

User = get_user_model()

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def server_error(request):
    return render(request, 'pages/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'pages/403.html', status=403)

def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

class ProfileView(ListView):
    model = Post
    template_name = 'pages/profile.html'
    context_object_name = 'posts'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user == self.profile_user:
            return Post.objects.filter(author=self.profile_user).select_related('category', 'location')
        else:
            return Post.objects.filter(author=self.profile_user, pub_date__lte=timezone.now()).select_related('category', 'location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

class AboutPage(TemplateView):
    template_name = 'pages/about.html'

class RulesPage(TemplateView):
    template_name = 'pages/rules.html'
