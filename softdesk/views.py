from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .services.chamados_service import ChamadoService
from .services.import_service import ImportSoftdeskService
from .models import SoftdeskChamado
from .serializers import SoftdeskChamadoSerializer
from helpdesk.serializers import ChamadoSerializer


# 🔹 1️⃣ Consulta direta na API Softdesk (sem salvar)
class SoftdeskChamadoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        cliente_id = request.data.get("cliente_id")
        codigo = request.data.get("codigo")

        if not cliente_id:
            return Response(
                {"erro": "cliente_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not codigo:
            return Response(
                {"erro": "codigo é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = ChamadoService.buscar_por_codigo(
                int(cliente_id),
                int(codigo)
            )

            return Response(data)

        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 🔹 2️⃣ Importar e salvar no banco
class SoftdeskImportarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        cliente_id = request.data.get("cliente_id")
        codigo = request.data.get("codigo")

        if not cliente_id or not codigo:
            return Response(
                {"erro": "cliente_id e codigo são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = ImportSoftdeskService.importar_chamado(
                int(cliente_id),
                int(codigo)
            )

            softdesk_serializer = SoftdeskChamadoSerializer(
                result["softdesk"]
            )

            chamado_serializer = ChamadoSerializer(
                result["chamado"]
            )

            return Response({
                "softdesk": softdesk_serializer.data,
                "chamado": chamado_serializer.data
            })

        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# 🔹 3️⃣ Listar chamados importados
class SoftdeskChamadoListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chamados = SoftdeskChamado.objects.all().order_by("-atualizado_em")
        serializer = SoftdeskChamadoSerializer(chamados, many=True)
        return Response(serializer.data)