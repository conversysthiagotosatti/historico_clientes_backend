from rest_framework.exceptions import PermissionDenied

def assert_contrato_access(user, contrato):
    # ajuste ao seu modelo real (tenant/cliente)
    # exemplo simples: se user tiver cliente associado
    if hasattr(user, "cliente_id") and user.cliente_id and contrato.cliente_id != user.cliente_id:
        raise PermissionDenied("Acesso negado a este contrato.")

def can_execute_actions(user) -> bool:
    # ajuste: grupo/permissão do Django
    return user.is_staff or user.has_perm("contratos.add_contratotarefa")
