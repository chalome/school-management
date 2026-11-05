from django.contrib.auth import views as auth_views
from django.urls import include, path

from .forms import UsernameOrEmailAuthenticationForm
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            authentication_form=UsernameOrEmailAuthenticationForm,
            template_name='registration/login.html',
        ),
        name='login',
    ),
    path('', include('django.contrib.auth.urls')),
]
