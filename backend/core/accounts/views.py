from django.urls import reverse_lazy
from django.views.generic import CreateView

from backend.core.accounts.forms import CustomUserCreationForm


class SignUpView(CreateView):
    http_method_names = ('GET', 'POST')
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

