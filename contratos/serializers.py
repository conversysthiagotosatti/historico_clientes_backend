from rest_framework import serializers
from .models import Contrato


class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = "__all__"
        read_only_fields = ["criado_em", "atualizado_em"]
