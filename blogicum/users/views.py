from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.shortcuts import render

User = get_user_model()


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class ProfileView(DetailView):
    model = User
    template_name = 'users/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')
    template_name = 'users/profile_edit.html'

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'username': self.object.username})

    def test_func(self):
        return self.request.user == self.get_object()

def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def permission_denied(request, exception=None):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def server_error(request):
    return render(request, "pages/500.html", status=500)


def bad_request(request, exception):
    return render(request, "pages/403csrf.html", status=400)