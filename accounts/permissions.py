from rest_framework.permissions import BasePermission, SAFE_METHODS
from accounts.tenant import get_cliente_context
from accounts.models import UserClienteRole

ROLE_RANK = {
    UserClienteRole.ANALISTA: 1,
    UserClienteRole.GERENTE_PROJETO: 2,
    UserClienteRole.LIDER: 3,
}

class HasClienteRoleAtLeast(BasePermission):
    required_role = UserClienteRole.ANALISTA

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        _, role = get_cliente_context(request)
        return ROLE_RANK.get(role, 0) >= ROLE_RANK.get(self.required_role, 0)

    @classmethod
    def required(cls, role):
        return type(f"HasRoleAtLeast_{role}", (cls,), {"required_role": role})


def get_user_profile(user):
    if hasattr(user, "profile"):
        return user.profile
    return None


class IsInterno(BasePermission):
    """
    Permite apenas usuários internos.
    """

    def has_permission(self, request, view):
        profile = get_user_profile(request.user)
        if not profile:
            return False
        return profile.tipo_usuario == "INTERNO"


class IsClienteOuInterno(BasePermission):
    """
    Permite internos sempre.
    Clientes apenas para objetos do próprio cliente.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        profile = get_user_profile(request.user)
        if not profile:
            return False

        # interno vê tudo
        if profile.tipo_usuario == "INTERNO":
            return True

        # cliente só vê objetos do próprio cliente
        cliente_id = profile.cliente_id
        if not cliente_id:
            return False

        # se objeto tem cliente direto
        if hasattr(obj, "cliente_id"):
            return obj.cliente_id == cliente_id

        # se objeto tem contrato
        if hasattr(obj, "contrato") and hasattr(obj.contrato, "cliente_id"):
            return obj.contrato.cliente_id == cliente_id

        # se objeto é equipe
        if hasattr(obj, "contratos"):
            return obj.contratos.filter(cliente_id=cliente_id).exists()

        return False


class PodeGerenciarEquipe(BasePermission):
    """
    Apenas interno pode criar/editar/excluir equipe.
    Cliente só pode visualizar.
    """

    def has_permission(self, request, view):
        profile = get_user_profile(request.user)
        if not profile:
            return False

        if request.method in SAFE_METHODS:
            return True

        return profile.tipo_usuario == "INTERNO"

    def has_object_permission(self, request, view, obj):
        profile = get_user_profile(request.user)
        if not profile:
            return False

        if request.method in SAFE_METHODS:
            return True

        return profile.tipo_usuario == "INTERNO"
