from rest_framework import serializers
from .models import (
    Setor, Chamado, ChamadoMensagem, ChamadoHistorico, 
    ChamadoApontamento, ChamadoTimer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = '__all__'

class ChamadoMensagemSerializer(serializers.ModelSerializer):
    autor_detalhes = UserSimpleSerializer(source='autor', read_only=True)

    class Meta:
        model = ChamadoMensagem
        fields = '__all__'

class ChamadoHistoricoSerializer(serializers.ModelSerializer):
    usuario_detalhes = UserSimpleSerializer(source='usuario', read_only=True)

    class Meta:
        model = ChamadoHistorico
        fields = '__all__'

class ChamadoApontamentoSerializer(serializers.ModelSerializer):
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)

    class Meta:
        model = ChamadoApontamento
        fields = '__all__'

class ChamadoTimerSerializer(serializers.ModelSerializer):
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)

    class Meta:
        model = ChamadoTimer
        fields = '__all__'

class ChamadoListSerializer(serializers.ModelSerializer):
    setor_detalhes = SetorSerializer(source='setor', read_only=True)
    solicitante_detalhes = UserSimpleSerializer(source='solicitante', read_only=True)
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)

    class Meta:
        model = Chamado
        fields = [
            'id', 'titulo', 'status', 'prioridade', 'setor', 'setor_detalhes', 
            'solicitante', 'solicitante_detalhes', 'atendente', 'atendente_detalhes', 
            'criado_em', 'atualizado_em', 'resolvido_em', 'sla_horas'
        ]

class ChamadoDetailSerializer(serializers.ModelSerializer):
    setor_detalhes = SetorSerializer(source='setor', read_only=True)
    solicitante_detalhes = UserSimpleSerializer(source='solicitante', read_only=True)
    atendente_detalhes = UserSimpleSerializer(source='atendente', read_only=True)
    # We won't nest all related items directly to avoid massive payloads, 
    # but we will provide summary data, or endpoints specifically for fetching messages/history.

    class Meta:
        model = Chamado
        fields = '__all__'
