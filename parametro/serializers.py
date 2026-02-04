from rest_framework import serializers
from .models import Parametro, ParametroCliente, ItensMonitoramento

class ParametroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametro
        fields = "__all__"


class ParametroClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametroCliente
        fields = "__all__"


class ItensMonitoramentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensMonitoramento
        fields = "__all__"
