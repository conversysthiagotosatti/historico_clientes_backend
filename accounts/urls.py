from django.urls import path
from .views import LoginWithClienteView, CreateUserView, MeClientsView, UserViewSet
from .view_users import CreateUserMultiClienteView
from .views_membership import AddMembershipView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
urlpatterns = router.urls
urlpatterns += [
    path("auth/novo_login/", LoginWithClienteView.as_view(), name="auth-login"),
    #path("auth/users/", CreateUserView.as_view(), name="auth-create-user"),
    path("auth/me/clients/", MeClientsView.as_view(), name="me-clients"),
    path("auth/users/", CreateUserMultiClienteView.as_view(), name="auth-create-user-multi"),
    path("auth/users/<int:user_id>/memberships/", AddMembershipView.as_view(), name="auth-add-membership"),
    
]

