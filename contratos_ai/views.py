from rest_framework.views import APIView
from rest_framework.response import Response
from .services.generator import gerar_documento
from .models import DocumentoGerado
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import ClausulaBase, DocumentoGerado
from rest_framework import status
from .services.clausula_ai import gerar_clausula_json
from .services.contrato_ai import gerar_contrato_por_prompt
from .serializers import (
    ClausulaBaseSerializer,
    DocumentoGeradoSerializer
)
from django.http import FileResponse
from .services.exportacao import exportar_contrato

class GerarContratoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")
        tipo_contrato = request.data.get("tipo_contrato")
        prompt_usuario = request.data.get("prompt")

        if not cliente_id or not tipo_contrato or not prompt_usuario:
            return Response(
                {"error": "cliente_id, tipo_contrato e prompt são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            documento = gerar_contrato_por_prompt(
                cliente_id=cliente_id,
                tipo_contrato=tipo_contrato,
                prompt_usuario=prompt_usuario,
                usuario=request.user
            )

            return Response(
                DocumentoGeradoSerializer(documento).data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
# ================================
# CLAUSULA BASE CRUD
# ================================

class ClausulaBaseViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClausulaBaseSerializer
    queryset = ClausulaBase.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()

        tipo = self.request.query_params.get("tipo")
        ativa = self.request.query_params.get("ativa")
        palavra = self.request.query_params.get("palavra")

        if tipo:
            qs = qs.filter(tipo=tipo)

        if ativa is not None:
            qs = qs.filter(ativa=ativa.lower() == "true")

        if palavra:
            qs = qs.filter(texto__icontains=palavra)

        return qs


# ================================
# DOCUMENTO GERADO CRUD
# ================================

class DocumentoGeradoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentoGeradoSerializer
    queryset = DocumentoGerado.objects.select_related(
        "cliente",
        "criado_por"
    ).all()

    def get_queryset(self):
        qs = super().get_queryset()

        cliente_id = self.request.query_params.get("cliente")
        tipo = self.request.query_params.get("tipo")
        criado_por = self.request.query_params.get("criado_por")

        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)

        if tipo:
            qs = qs.filter(tipo=tipo)

        if criado_por:
            qs = qs.filter(criado_por_id=criado_por)

        return qs
    
class GerarClausulaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")
        descricao = request.data.get("descricao")

        if not cliente_id or not descricao:
            return Response(
                {"error": "cliente_id e descricao são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 1️⃣ Gera JSON via IA
            dados = gerar_clausula_json(cliente_id, descricao)

            # 2️⃣ Validação via serializer
            serializer = ClausulaBaseSerializer(data=dados)

            if serializer.is_valid():
                clausula = serializer.save()
                return Response(
                    {
                        "message": "Cláusula criada com sucesso.",
                        "clausula": ClausulaBaseSerializer(clausula).data
                    },
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GerarContratoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")
        tipo_contrato = request.data.get("tipo_contrato")
        prompt_usuario = request.data.get("prompt")

        if not cliente_id or not tipo_contrato or not prompt_usuario:
            return Response(
                {"error": "cliente_id, tipo_contrato e prompt são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            documento = gerar_contrato_por_prompt(
                cliente_id=cliente_id,
                tipo_contrato=tipo_contrato,
                prompt_usuario=prompt_usuario,
                usuario=request.user
            )

            return Response(
                {
                    "message": "Contrato gerado com sucesso.",
                    "documento": DocumentoGeradoSerializer(documento).data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ExportarContratoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, documento_id):
        formato = request.query_params.get("formato", "pdf")

        caminho = exportar_contrato(documento_id, formato)

        return FileResponse(
            open(caminho, "rb"),
            as_attachment=True
        )