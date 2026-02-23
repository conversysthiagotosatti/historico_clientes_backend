from rest_framework import serializers
from .models import Contrato, ContratoTarefa, ContratoClausula


class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em"]


class ContratoTarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoTarefa
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em"]

class ContratoClausulaSerializer(serializers.ModelSerializer):
    contrato_id = serializers.IntegerField(source="contrato.id", read_only=True)
    fonte_arquivo_id = serializers.IntegerField(source="fonte_arquivo.id", read_only=True)

    class Meta:
        model = ContratoClausula
        fields = [
            "id",
            "contrato", "contrato_id",
            "fonte_arquivo", "fonte_arquivo_id",
            "numero", "titulo", "texto", "ordem",
            "extraida_por_ia", "confidence", "raw",
            "criado_em", "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]