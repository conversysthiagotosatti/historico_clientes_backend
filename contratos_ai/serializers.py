from rest_framework import serializers
from .models import ClausulaBase, DocumentoGerado, MemoriaCalculo, MemoriaCalculoItem


# ================================
# CLAUSULA BASE
# ================================

class ClausulaBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClausulaBase
        fields = "__all__"


# ================================
# DOCUMENTO GERADO
# ================================

class DocumentoGeradoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(
        source="cliente.nome",
        read_only=True
    )

    class Meta:
        model = DocumentoGerado
        fields = "__all__"


# ================================
# MEMÓRIA DE CÁLCULO
# ================================


class MemoriaCalculoItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoriaCalculoItem
        fields = "__all__"


class MemoriaCalculoSerializer(serializers.ModelSerializer):
    itens = MemoriaCalculoItemSerializer(many=True)

    class Meta:
        model = MemoriaCalculo
        fields = "__all__"

    def create(self, validated_data):
        itens_data = validated_data.pop("itens", [])
        memoria = MemoriaCalculo.objects.create(**validated_data)

        for item_data in itens_data:
            MemoriaCalculoItem.objects.create(memoria=memoria, **item_data)

        return memoria