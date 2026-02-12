from django.urls import path
from .views import LoginWithClienteView, CreateUserView

urlpatterns = [
    path("auth/novo_login/", LoginWithClienteView.as_view(), name="auth-login"),
    path("auth/users/", CreateUserView.as_view(), name="auth-create-user")
]
