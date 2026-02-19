# contratos/views_copilot.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from copilot.contracts.service import responder_pergunta_contrato

class CopilotContratoQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contrato_id: int):
        pergunta = (request.data.get("message") or "").strip()
        if not pergunta:
            return Response({"detail": "Envie 'message'."}, status=status.HTTP_400_BAD_REQUEST)

        data = responder_pergunta_contrato(user=request.user, contrato_id=contrato_id, pergunta=pergunta)
        return Response(data, status=status.HTTP_200_OK)
