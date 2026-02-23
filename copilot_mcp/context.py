from dataclasses import dataclass
from django.contrib.auth import get_user_model
from clientes.models import Cliente
from contratos.models import Contrato

User = get_user_model()

@dataclass(frozen=True)
class Identity:
    user: User
    cliente: Cliente
    contrato: Contrato
    prompt_version: str = "mcp-v1"
    model: str = "unknown"