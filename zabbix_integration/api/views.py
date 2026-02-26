from urllib import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from zabbix_integration.dashboards.executivo import zabbix_dashboard_executivo
from .serializers import (
    DashboardExecutivoRequestSerializer,
    DashboardExecutivoResponseSerializer,
)
from zabbix_integration.services.sync_hostgroups import sync_hostgroups

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