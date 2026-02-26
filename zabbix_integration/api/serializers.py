from rest_framework import serializers


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