from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import (
    Setor, Chamado, ChamadoMensagem, ChamadoHistorico, 
    ChamadoApontamento, ChamadoTimer, ChamadoTimerEstado
)
from .serializers import (
    SetorSerializer, ChamadoListSerializer, ChamadoDetailSerializer,
    ChamadoMensagemSerializer, ChamadoHistoricoSerializer,
    ChamadoApontamentoSerializer, ChamadoTimerSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import datetime

class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    pagination_class = None

class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamado.objects.select_related('setor', 'solicitante', 'atendente')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'setor', 'prioridade', 'solicitante', 'atendente']
    search_fields = ['titulo', 'descricao', 'id']
    ordering_fields = ['criado_em', 'atualizado_em', 'prioridade', 'status']
    ordering = ['-atualizado_em']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChamadoListSerializer
        return ChamadoDetailSerializer

    def perform_create(self, serializer):
        solicitante_id = self.request.data.get('solicitante_id')
        solicitante = self.request.user
        
        # Permitir que um ATENDENTE crie o chamado em nome de outro usuario (Cliente)
        if solicitante_id and self.request.user.is_staff: # Simplificando validacao de atendente por `is_staff`
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                solicitante = User.objects.get(pk=solicitante_id)
            except User.DoesNotExist:
                pass
                
        serializer.save(solicitante=solicitante)

    @action(detail=True, methods=['get'])
    def mensagens(self, request, pk=None):
        chamado = self.get_object()
        mensagens = chamado.mensagens.select_related('autor').all()
        serializer = ChamadoMensagemSerializer(mensagens, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_mensagem(self, request, pk=None):
        chamado = self.get_object()
        conteudo = request.data.get('conteudo')
        tipo_autor = request.data.get('tipo_autor', 'SISTEMA')
        
        if not conteudo:
            return Response({"error": "Conteudo invalido"}, status=status.HTTP_400_BAD_REQUEST)
            
        mensagem = ChamadoMensagem.objects.create(
            chamado=chamado,
            autor=request.user,
            tipo_autor=tipo_autor,
            conteudo=conteudo
        )
        return Response(ChamadoMensagemSerializer(mensagem).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        chamado = self.get_object()
        hist = chamado.historico.select_related('usuario').all()
        serializer = ChamadoHistoricoSerializer(hist, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def apontamentos(self, request, pk=None):
        chamado = self.get_object()
        apont = chamado.apontamentos.select_related('atendente').all()
        serializer = ChamadoApontamentoSerializer(apont, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_apontamento(self, request, pk=None):
        chamado = self.get_object()
        horas = request.data.get('horas')
        descricao = request.data.get('descricao')
        data_apontamento = request.data.get('data', datetime.date.today())

        if not horas or not descricao:
            return Response({"error": "Horas e descricao sao obrigatorios."}, status=status.HTTP_400_BAD_REQUEST)

        apontamento = ChamadoApontamento.objects.create(
            chamado=chamado,
            atendente=request.user,
            data=data_apontamento,
            horas=horas,
            descricao=descricao
        )
        return Response(ChamadoApontamentoSerializer(apontamento).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def mudar_status(self, request, pk=None):
        chamado = self.get_object()
        novo_status = request.data.get('status')
        observacao = request.data.get('observacao')

        if not novo_status:
            return Response({"error": "Status obrigatorio."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar choices
        from .models import ChamadoStatus
        if novo_status not in dict(ChamadoStatus.choices).keys():
             return Response({"error": "Status invalido."}, status=status.HTTP_400_BAD_REQUEST)

        chamado.status = novo_status
        if novo_status in ["RESOLVIDO", "FECHADO"]:
             chamado.resolvido_em = timezone.now()

        # O Signal criar o Historico automaticamente. Passaremos a observacao via contexto hack ou atualizando dps.
        # Melhor: atualizar o Historico que o Signal acabou de criar.
        
        chamado.save()
        
        if observacao:
             # Pega o ultimo historico criado para este chamado
             ultimo_hist = chamado.historico.order_by('-criado_em').first()
             if ultimo_hist:
                 ultimo_hist.observacao = observacao
                 ultimo_hist.save()

        return Response(ChamadoDetailSerializer(chamado).data)


class ChamadoTimerViewSet(viewsets.ViewSet):
    """
    Endpoints customizados para gerenciar o Timer do Atendente.
    """
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        chamado_id = pk
        chamado = Chamado.objects.get(pk=chamado_id)
        
        timer, created = ChamadoTimer.objects.get_or_create(
            chamado=chamado, 
            atendente=request.user
        )
        
        if timer.estado == ChamadoTimerEstado.RODANDO:
            return Response({"message": "Timer ja esta rodando."}, status=status.HTTP_400_BAD_REQUEST)

        # Inicia o timer
        timer.estado = ChamadoTimerEstado.RODANDO
        timer.iniciado_em = timezone.now()
        timer.save()
        
        return Response(ChamadoTimerSerializer(timer).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        chamado_id = pk
        try:
            timer = ChamadoTimer.objects.get(chamado_id=chamado_id, atendente=request.user)
        except ChamadoTimer.DoesNotExist:
            return Response({"error": "Timer nao encontrado."}, status=status.HTTP_404_NOT_FOUND)
            
        if timer.estado == ChamadoTimerEstado.PAUSADO:
            return Response({"message": "Timer ja esta pausado."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Calcula segundos passados
        if timer.iniciado_em:
            delta = timezone.now() - timer.iniciado_em
            timer.tempo_acumulado_segundos += int(delta.total_seconds())
            
        timer.estado = ChamadoTimerEstado.PAUSADO
        timer.iniciado_em = None
        timer.save()
        
        return Response(ChamadoTimerSerializer(timer).data)

    @action(detail=True, methods=['post'])
    def finalizar_apontamento(self, request, pk=None):
        chamado_id = pk
        descricao = request.data.get('descricao', 'Apontamento automático do timer.')
        
        try:
            timer = ChamadoTimer.objects.get(chamado_id=chamado_id, atendente=request.user)
        except ChamadoTimer.DoesNotExist:
            return Response({"error": "Timer nao encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Se estava rodando, acumula o tempo restante antes de zerar
        if timer.estado == ChamadoTimerEstado.RODANDO and timer.iniciado_em:
            delta = timezone.now() - timer.iniciado_em
            timer.tempo_acumulado_segundos += int(delta.total_seconds())
            
        total_segundos = timer.tempo_acumulado_segundos
        if total_segundos < 60:
            return Response({"error": "Tempo acumulado insuficiente (< 1 min)."}, status=status.HTTP_400_BAD_REQUEST)
            
        horas_decimais = round(total_segundos / 3600.0, 2)
        
        # Cria apontamento
        apontamento = ChamadoApontamento.objects.create(
            chamado_id=chamado_id,
            atendente=request.user,
            data=datetime.date.today(),
            horas=horas_decimais,
            descricao=descricao
        )
        
        # Reseta o timer
        timer.tempo_acumulado_segundos = 0
        timer.estado = ChamadoTimerEstado.PAUSADO
        timer.iniciado_em = None
        timer.save()
        
        return Response({
            "message": "Apontamento gerado com sucesso.",
            "apontamento": ChamadoApontamentoSerializer(apontamento).data,
            "timer": ChamadoTimerSerializer(timer).data
        })
