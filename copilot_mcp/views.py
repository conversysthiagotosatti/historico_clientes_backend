from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .auth import resolve_identity_from_headers
from .router import execute_tool

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