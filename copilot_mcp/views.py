from __future__ import annotations

from rest_framework import status

from .auth import resolve_identity_from_headers

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from openai import OpenAI

from .openai_tools import TOOLS, OPENAI_TO_INTERNAL
from .router import execute_tool
from django.core.serializers.json import DjangoJSONEncoder


SYSTEM_INSTRUCTIONS = """
Você é o Copilot do módulo de Contratos.
Quando o usuário pedir para listar contratos, listar arquivos, extrair cláusulas ou gerar tarefas,
você DEVE usar as ferramentas disponíveis.
Nunca invente IDs. Se não tiver contrato_id ou contrato_arquivo_id, use as tools de listagem/consulta para descobrir.
Se ainda assim faltar informação, pergunte objetivamente ao usuário.
Responda em pt-BR, curto e direto.
""".strip()


class CopilotChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_text = (request.data.get("message") or "").strip()
        if not user_text:
            return Response({"ok": False, "message": "Campo 'message' é obrigatório."}, status=400)

        client = OpenAI()

        # 1) PRIMEIRA CHAMADA — se falhar, retorna erro e não entra no loop
        try:
            resp = client.responses.create(
                model="gpt-4.1",
                instructions=SYSTEM_INSTRUCTIONS,
                input=user_text,
                tools=TOOLS,
            )
        except Exception as e:
            return Response(
                {"ok": False, "message": "Falha ao chamar o modelo.", "data": {"detail": str(e)}},
                status=502,
            )

        # 2) LOOP DE TOOLS (limite para não travar)
        for _ in range(8):
            output_items = resp.output or []
            function_calls = [it for it in output_items if getattr(it, "type", None) == "function_call"]

            if not function_calls:
                # sem tools: finaliza
                return Response({"ok": True, "answer": resp.output_text})

            tool_outputs = []
            for call in function_calls:
                fn_name = getattr(call, "name", None)
                call_id = getattr(call, "call_id", None)
                raw_args = getattr(call, "arguments", None) or "{}"

                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {}

                internal_tool = OPENAI_TO_INTERNAL.get(fn_name)
                if not internal_tool:
                    result = {"ok": False, "message": f"Tool {fn_name} não mapeada no backend."}
                else:
                    result = execute_tool(tool=internal_tool, args=args, user=user)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result, ensure_ascii=False, cls=DjangoJSONEncoder),
                })

            # 3) CONTINUAÇÃO — só envia outputs e usa previous_response_id do resp atual
            try:
                resp = client.responses.create(
                    model="gpt-4.1",
                    previous_response_id=resp.id,
                    input=tool_outputs,
                    tools=TOOLS,
                )
            except Exception as e:
                return Response(
                    {"ok": False, "message": "Falha ao continuar execução de tools.", "data": {"detail": str(e)}},
                    status=502,
                )

        # Se chegou aqui, estourou limite de iterações
        return Response(
            {"ok": False, "message": "Limite de chamadas de ferramentas excedido."},
            status=400
        )

class MCPExecuteView(APIView):
    """
    Recebe:
      { "tool": "contratos.extrair_clausulas", "args": {...} }
    """
    authentication_classes = []  # vamos validar JWT manualmente
    permission_classes = []      # idem

    def post(self, request):
        try:
            identity = resolve_identity_from_headers(request.headers)
        except PermissionError as e:
            return Response({"ok": False, "message": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        tool = request.data.get("tool")
        args = request.data.get("args") or {}

        if not tool:
            return Response({"ok": False, "message": "Campo 'tool' é obrigatório."}, status=400)

        try:
            result = execute_tool(tool=tool, args=args, user=identity.user)
            return Response(result, status=200 if result.get("ok") else 400)
        except Exception as e:
            return Response({"ok": False, "message": "Erro interno.", "data": {"detail": str(e)}}, status=500)