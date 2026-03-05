from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import FileResponse
import os

from zabbix_integration.dashboards.executivo import zabbix_dashboard_executivo
from zabbix_integration.services.sync_hostgroups import sync_hostgroups
from zabbix_integration.services.sync_hosts import sync_hosts
from zabbix_integration.services.relatorio_eventos import gerar_relatorio_eventos_recovery
from zabbix_integration.services.sync_items import sync_items_enterprise
from zabbix_integration.services.sync_level2 import sync_history
from zabbix_integration.models import ZabbixItem

from .serializers import (
    DashboardExecutivoRequestSerializer,
    DashboardExecutivoResponseSerializer,
    SyncItemsRequestSerializer,
    SyncHistoryRequestSerializer,
    ZabbixItemSerializer,
)


class ZabbixDashboardExecutivoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DashboardExecutivoRequestSerializer(data=request.data)
        print(request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        print(data)
        try:
            dashboard = zabbix_dashboard_executivo(
                cliente_id=data["cliente_id"],
                ano=data["ano"],
                mes=data["mes"],
            )

            response_serializer = DashboardExecutivoResponseSerializer(dashboard)

            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Erro ao gerar dashboard executivo: {e}")
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SyncHostGroupsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")

        if not cliente_id:
            return Response(
                {"erro": "cliente_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = sync_hostgroups(int(cliente_id))
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RelatorioEventosRecoveryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cliente_id = request.data.get("cliente_id")

        if not cliente_id:
            return Response(
                {"erro": "cliente_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            caminho = gerar_relatorio_eventos_recovery(int(cliente_id))

            return FileResponse(
                open(caminho, "rb"),
                as_attachment=True,
                filename=os.path.basename(caminho)
            )

        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SyncZabbixItemsAPIView(APIView):
    """
    POST /zabbix/sync/items/
    Body: { "cliente_id": <int> }
    Dispara a sincronização das métricas (ZabbixItem) a partir do Zabbix.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SyncItemsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cliente_id = serializer.validated_data["cliente_id"]

        try:
            resultado = sync_items_enterprise(cliente_id)
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SyncZabbixHostsAPIView(APIView):
    """
    POST /zabbix/sync/hosts/
    Body: { "cliente_id": <int> }
    Dispara a sincronização dos hosts a partir do Zabbix.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SyncItemsRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cliente_id = serializer.validated_data["cliente_id"]

        try:
            sync_hosts(cliente_id)
            return Response(
                {"mensagem": f"Sincronização de hosts iniciada para cliente {cliente_id}."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SyncZabbixHistoryAPIView(APIView):
    """
    POST /zabbix/sync/history/
    Body:
    {
      "cliente_id": 1,
      "itemids": ["23635", "23636"],   # opcional
      "host_id": "12345",              # opcional (hostid do Zabbix)
      "hours": 24                      # opcional, padrão 24h
    }

    Se `itemids` não for informado, sincroniza histórico de todos os itens
    do cliente (filtrados por `host_id` se enviado) na janela de tempo.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SyncHistoryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        cliente_id = data["cliente_id"]
        itemids = data.get("itemids") or []
        host_id = data.get("host_id") or None
        hours = data.get("hours") or 24

        from datetime import datetime, timedelta, timezone

        time_till = datetime.now(tz=timezone.utc)
        time_from = time_till - timedelta(hours=hours)

        # Se não vier lista de itemids, descobrimos pelos itens locais
        if not itemids:
            qs = ZabbixItem.objects.filter(cliente_id=cliente_id)
            if host_id:
                qs = qs.filter(host__hostid=str(host_id))
            itemids = list(qs.values_list("itemid", flat=True))

        if not itemids:
            return Response(
                {"erro": "Nenhum item encontrado para sincronizar histórico."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sync_history(cliente_id, itemids, time_from, time_till)
            return Response(
                {
                    "mensagem": "Histórico sincronizado com sucesso.",
                    "cliente_id": cliente_id,
                    "total_itens": len(itemids),
                    "periodo": {
                        "time_from": time_from.isoformat(),
                        "time_till": time_till.isoformat(),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"erro": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ZabbixMetricsListAPIView(APIView):
    """
    GET /zabbix/metrics/?cliente_id=1&host_id=123&year=2026&month=2&search=cpu&limit=50&offset=0
    Lista métricas (itens) já sincronizadas no banco.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cliente_id = request.query_params.get("cliente_id")
        if not cliente_id:
            return Response(
                {"erro": "cliente_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = ZabbixItem.objects.select_related("host").filter(
            cliente_id=int(cliente_id),
        )

        host_id = request.query_params.get("host_id")
        if host_id:
            qs = qs.filter(host__hostid=str(host_id))

        # Filtro por ano/mês usando o campo lastclock do item
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        if year:
            try:
                qs = qs.filter(lastclock__year=int(year))
            except ValueError:
                return Response(
                    {"erro": "year deve ser inteiro"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if month:
            try:
                qs = qs.filter(lastclock__month=int(month))
            except ValueError:
                return Response(
                    {"erro": "month deve ser inteiro"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search)

        try:
            limit = int(request.query_params.get("limit", 50))
            offset = int(request.query_params.get("offset", 0))
        except ValueError:
            return Response(
                {"erro": "limit e offset devem ser inteiros"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = qs.count()
        itens = qs.order_by("id")[offset: offset + limit]

        serializer = ZabbixItemSerializer(itens, many=True)
        return Response(
            {
                "count": total,
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )