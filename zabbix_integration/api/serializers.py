from rest_framework import serializers
from zabbix_integration.models import ZabbixItem


class DashboardExecutivoRequestSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    ano = serializers.IntegerField()
    mes = serializers.IntegerField()


class TopHostSerializer(serializers.Serializer):
    host = serializers.CharField()
    incidentes = serializers.IntegerField()


class DashboardExecutivoResponseSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()
    periodo = serializers.CharField()
    sla_geral = serializers.FloatField()
    disponibilidade_media = serializers.FloatField()
    total_incidentes = serializers.IntegerField()
    eventos_criticos = serializers.IntegerField()
    mttr_medio_minutos = serializers.FloatField()
    top_hosts_criticos = TopHostSerializer(many=True)
    resumo_executivo = serializers.CharField()


class SyncItemsRequestSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField()


class SyncHistoryRequestSerializer(serializers.Serializer):
    """
    Payload para sincronizar histórico (ZabbixHistory) a partir do Zabbix.

    Se `itemids` não for informado, serão usados todos os itens do cliente
    (opcionalmente filtrados por `host_id`).
    """

    cliente_id = serializers.IntegerField()
    itemids = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    host_id = serializers.CharField(required=False, allow_blank=True)
    hours = serializers.IntegerField(required=False, min_value=1, default=24)


class ZabbixItemSerializer(serializers.ModelSerializer):
    host_nome = serializers.CharField(source="host.nome", read_only=True)
    host_ip = serializers.CharField(source="host.ip", read_only=True)

    class Meta:
        model = ZabbixItem
        fields = [
            "id",
            "cliente_id",
            "itemid",
            "name",
            "key",
            "units",
            "lastvalue",
            "lastclock",
            "enabled",
            "host_nome",
            "host_ip",
        ]