from __future__ import annotations
from typing import Callable

from .tools_contratos import (
    contratos_listar,
    contratos_get,
    contratos_arquivos_listar,
    contratos_extrair_clausulas,
    contratos_gerar_tarefas,
)

TOOL_REGISTRY: dict[str, Callable] = {
    "contratos.listar": contratos_listar,
    "contratos.get": contratos_get,
    "contratos.arquivos_listar": contratos_arquivos_listar,
    "contratos.extrair_clausulas": contratos_extrair_clausulas,
    "contratos.gerar_tarefas": contratos_gerar_tarefas,
}

def execute_tool(*, tool: str, args: dict, user) -> dict:
    fn = TOOL_REGISTRY.get(tool)
    if not fn:
        return {"ok": False, "message": "Tool não suportada.", "error_code": "TOOL_NOT_FOUND"}
    return fn(user=user, **args)