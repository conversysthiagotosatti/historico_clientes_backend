from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from contratos.models import ContratoArquivo
from .serializers import ContratoArquivoSerializer

class ContratoArquivoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContratoArquivoSerializer

    queryset = (
        ContratoArquivo.objects
        .select_related("contrato", "extraido_por")
        .all()
    )

    def get_queryset(self):
        qs = super().get_queryset()

        contrato_id = self.request.query_params.get("contrato")
        tipo = self.request.query_params.get("tipo")
        versao = self.request.query_params.get("versao")

        if contrato_id:
            qs = qs.filter(contrato_id=int(contrato_id))

        if tipo:
            qs = qs.filter(tipo=tipo)

        if versao:
            qs = qs.filter(versao=int(versao))

        return qs