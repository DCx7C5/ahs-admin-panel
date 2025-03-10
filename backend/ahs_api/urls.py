from django.urls import path

from backend.ahs_api.views import LoginView, SignupView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
]
