from rest_framework import serializers
from .models import ClausulaBase, DocumentoGerado


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