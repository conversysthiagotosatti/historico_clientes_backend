from __future__ import annotations

from typing import Callable
from django.core.exceptions import PermissionDenied

from .tools_contratos import (
    contratos_criar,
    contratos_extrair_clausulas,
    contratos_gerar_tarefas,
)

TOOL_REGISTRY: dict[str, Callable] = {
    "contratos.criar": contratos_criar,
    "contratos.extrair_clausulas": contratos_extrair_clausulas,
    "contratos.gerar_tarefas": contratos_gerar_tarefas,
}

def execute_tool(*, tool: str, args: dict, user):
    fn = TOOL_REGISTRY.get(tool)
    if not fn:
        return {"ok": False, "message": "Tool não suportada.", "error_code": "TOOL_NOT_FOUND"}

    return fn(user=user, **args)