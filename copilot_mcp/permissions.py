from django.core.exceptions import PermissionDenied
from contratos.models import Contrato

def assert_contrato_scope(user, contrato: Contrato, cliente_id: int):
    # garante coerência
    if contrato.cliente_id != cliente_id:
        raise PermissionDenied("Contrato não pertence ao cliente informado.")

    # aqui você pode colocar regras por tenant/grupo
    # exemplo: user precisa ter permissão e acesso ao cliente
    # ajuste para seu auth real
    if not user.is_authenticated:
        raise PermissionDenied("Usuário não autenticado.")

def assert_perm(user, perm_codename: str):
    # padronize suas perms: "contratos.add_contrato" etc.
    if not user.has_perm(perm_codename):
        raise PermissionDenied(f"Sem permissão: {perm_codename}")