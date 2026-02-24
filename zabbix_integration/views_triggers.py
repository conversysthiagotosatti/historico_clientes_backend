# zabbix_integration/views_triggers.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ZabbixTrigger
from .serializers import ZabbixTriggerSerializer
from .servico import sync_triggers

class ZabbixTriggersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente_id = request.query_params.get("cliente")
        if not cliente_id:
            return Response({"detail": "Informe ?cliente=ID"}, status=400)

        qs = ZabbixTrigger.objects.filter(cliente_id=int(cliente_id)).order_by("-ultima_alteracao")
        return Response(ZabbixTriggerSerializer(qs, many=True).data)

class ZabbixSyncTriggersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        cliente_id = data.get("cliente")
        item_key = data.get("item")

        if not cliente_id:
            return Response(
                {"detail": "Campo 'cliente' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not item_key:
            return Response(
                {"detail": "Campo 'item' é obrigatório (key do item)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cliente_id = int(cliente_id)
        except ValueError:
            return Response(
                {"detail": "Campo 'cliente' deve ser inteiro"},
                status=status.HTTP_400_BAD_REQUEST
            )

        filtros = {
            "description": data.get("description"),
            "priority": data.get("priority"),
            "status": data.get("status"),
        }

        summary = sync_triggers(
            cliente_id=cliente_id,
            item_key=item_key,
            filtros=filtros
        ) or {}

        return Response({
            "detail": "Triggers sincronizadas",
            **summary
        })