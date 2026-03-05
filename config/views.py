from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import gerar_token_graph
from config.services_cidades import importar_cidades_soft4


class ImportarCidadesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")

        if not cliente_id:
            return Response(
                {"erro": "cliente_id é obrigatório"},
                status=400
            )

        resultado = importar_cidades_soft4(cliente_id)

        return Response(resultado)

class TestarTokenGraphView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        token_data = gerar_token_graph()

        return Response({
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "access_token_inicio": token_data.get("access_token")[:50]  # só preview
        })