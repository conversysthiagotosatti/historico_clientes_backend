from rest_framework import serializers
from .models import Tarefa, Apontamento

class ApontamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apontamento
        fields = "__all__"


class TarefaSerializer(serializers.ModelSerializer):
    horas_consumidas = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Tarefa
        fields = "__all__"
