from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import datetime

from .models import (
    Setor,
    Chamado, ChamadoMensagem, ChamadoHistorico,
    ChamadoApontamento, ChamadoTimer, ChamadoTimerEstado, ChamadoStatus,
    Cidade, Empresa, ClienteHelpdesk, Departamento, Filial,
    UsuarioHelpdesk, ContratoHelpdesk, AnexoContrato, Atendente,
    AtividadeChamado, AnexoChamado,
    Categoria, Servico, PrioridadeHelpdesk, StatusChamadoConfig,
    TipoChamado, Area, GrupoSolucao, Impacto, TemaTemplate, TemplateChamado,
    ItemConfiguracao, CampoCustomizavelIC, ValorCampoIC,
    Fornecedor, CentroCusto,
    FAQ, AnexoFAQ,
    Ligacao, PesquisaSatisfacao, ContestacaoChamado, FechamentoAvaliacao,
    FormularioAprovacao, CampoFormulario, ConfiguracaoAnexo,
)

from .serializers import (
    SetorSerializer,
    ChamadoSerializer, ChamadoListSerializer, ChamadoDetailSerializer,
    ChamadoMensagemSerializer, ChamadoHistoricoSerializer,
    ChamadoApontamentoSerializer, ChamadoTimerSerializer,
    CidadeSerializer, EmpresaSerializer,
    ClienteHelpdeskSerializer, ClienteHelpdeskListSerializer,
    DepartamentoSerializer, FilialSerializer,
    UsuarioHelpdeskSerializer, ContratoHelpdeskSerializer, AnexoContratoSerializer,
    AtendenteSerializer, AtividadeChamadoSerializer, AnexoChamadoSerializer,
    CategoriaSerializer, ServicoSerializer, PrioridadeHelpdeskSerializer,
    StatusChamadoConfigSerializer, TipoChamadoSerializer, AreaSerializer,
    GrupoSolucaoSerializer, ImpactoSerializer, TemaTemplateSerializer,
    TemplateChamadoSerializer,
    ItemConfiguracaoSerializer, CampoCustomizavelICSerializer, ValorCampoICSerializer,
    FornecedorSerializer, CentroCustoSerializer,
    FAQSerializer, AnexoFAQSerializer,
    LigacaoSerializer, PesquisaSatisfacaoSerializer,
    ContestacaoChamadoSerializer, FechamentoAvaliacaoSerializer,
    FormularioAprovacaoSerializer, CampoFormularioSerializer,
    ConfiguracaoAnexoSerializer,
)


# =============================================
# Setor
# =============================================
class SetorViewSet(viewsets.ModelViewSet):
    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    pagination_class = None


# =============================================
# Chamado (expandido)
# =============================================
class ChamadoViewSet(viewsets.ModelViewSet):
    queryset = Chamado.objects.select_related(
        'setor', 'solicitante', 'atendente',
        'categoria', 'servico', 'tipo_chamado', 'area',
        'cliente_helpdesk', 'impacto', 'grupo_solucao', 'atendente_helpdesk',
    )
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'status', 'setor', 'prioridade', 'solicitante', 'atendente',
        'categoria', 'servico', 'tipo_chamado', 'area',
        'cliente_helpdesk', 'filial', 'contrato_helpdesk',
        'centro_custo', 'impacto', 'grupo_solucao', 'atendente_helpdesk',
        'codigo_integracao',
    ]
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

        if solicitante_id and self.request.user.is_staff:
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

        if novo_status not in dict(ChamadoStatus.choices).keys():
            return Response({"error": "Status invalido."}, status=status.HTTP_400_BAD_REQUEST)

        chamado.status = novo_status
        if novo_status in ["RESOLVIDO", "FECHADO"]:
            chamado.resolvido_em = timezone.now()

        chamado.save()

        if observacao:
            ultimo_hist = chamado.historico.order_by('-criado_em').first()
            if ultimo_hist:
                ultimo_hist.observacao = observacao
                ultimo_hist.save()

        return Response(ChamadoDetailSerializer(chamado).data)

    @action(detail=True, methods=['post'])
    def assumir(self, request, pk=None):
        chamado = self.get_object()
        
        # Opcional: validar se ja tem atendente
        if chamado.atendente:
            if chamado.atendente == request.user:
                return Response({"message": "Voce ja e o atendente deste chamado."}, status=status.HTTP_400_BAD_REQUEST)
            # Pode ou nao permitir roubar o chamado, aqui vamos permitir mas registrar no historico
        
        atendente_anterior = chamado.atendente
        
        chamado.atendente = request.user
        if not chamado.status or chamado.status == "ABERTO":
            chamado.status = "EM_ATENDIMENTO"
        
        chamado.save()

        # Registrar no historico
        msg = "Assumiu o chamado."
        if atendente_anterior:
            msg = f"Assumiu o chamado (anterior: {atendente_anterior.get_full_name() or atendente_anterior.username})."
            
        ChamadoHistorico.objects.create(
            chamado=chamado,
            status_anterior=chamado.status,
            status_novo=chamado.status,
            usuario=request.user,
            observacao=msg
        )

        return Response(ChamadoDetailSerializer(chamado).data)

    @action(detail=True, methods=['post'])
    def transferir(self, request, pk=None):
        chamado = self.get_object()
        novo_atendente_id = request.data.get('atendente_id')
        
        if not novo_atendente_id:
            return Response({"error": "ID do novo atendente e obrigatorio."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            novo_atendente = User.objects.get(id=novo_atendente_id)
        except User.DoesNotExist:
            return Response({"error": "Usuario nao encontrado."}, status=status.HTTP_404_NOT_FOUND)

        atendente_anterior = chamado.atendente
        
        chamado.atendente = novo_atendente
        chamado.save()

        msg = f"Chamado transferido para {novo_atendente.get_full_name() or novo_atendente.username}."
        
        ChamadoHistorico.objects.create(
            chamado=chamado,
            status_anterior=chamado.status,
            status_novo=chamado.status,
            usuario=request.user,
            observacao=msg
        )

        return Response(ChamadoDetailSerializer(chamado).data)

    # Atividades
    @action(detail=True, methods=['get'])
    def atividades(self, request, pk=None):
        chamado = self.get_object()
        atividades = chamado.atividades.select_related('atendente', 'usuario').all()
        serializer = AtividadeChamadoSerializer(atividades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_atividade(self, request, pk=None):
        chamado = self.get_object()
        data = request.data.copy()
        data['chamado'] = chamado.id
        serializer = AtividadeChamadoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Anexos
    @action(detail=True, methods=['get'])
    def anexos(self, request, pk=None):
        chamado = self.get_object()
        anexos = chamado.anexos.all()
        serializer = AnexoChamadoSerializer(anexos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_anexo(self, request, pk=None):
        chamado = self.get_object()
        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({"error": "Arquivo obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        anexo = AnexoChamado.objects.create(
            chamado=chamado,
            arquivo=arquivo,
            nome_original=arquivo.name,
            tamanho_bytes=arquivo.size,
            mime_type=arquivo.content_type,
            descricao=request.data.get('descricao', ''),
        )
        return Response(AnexoChamadoSerializer(anexo).data, status=status.HTTP_201_CREATED)

    # Ligações
    @action(detail=True, methods=['get'])
    def ligacoes(self, request, pk=None):
        chamado = self.get_object()
        serializer = LigacaoSerializer(chamado.ligacoes.all(), many=True)
        return Response(serializer.data)

    # Pesquisas de satisfação
    @action(detail=True, methods=['get', 'post'])
    def satisfacao(self, request, pk=None):
        chamado = self.get_object()
        if request.method == 'GET':
            serializer = PesquisaSatisfacaoSerializer(chamado.pesquisas_satisfacao.all(), many=True)
            return Response(serializer.data)
        else:
            data = request.data.copy()
            data['chamado'] = chamado.id
            serializer = PesquisaSatisfacaoSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Contestações
    @action(detail=True, methods=['get', 'post'])
    def contestacoes(self, request, pk=None):
        chamado = self.get_object()
        if request.method == 'GET':
            serializer = ContestacaoChamadoSerializer(chamado.contestacoes.all(), many=True)
            return Response(serializer.data)
        else:
            data = request.data.copy()
            data['chamado'] = chamado.id
            serializer = ContestacaoChamadoSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Fechamento com avaliação
    @action(detail=True, methods=['post'])
    def fechar_com_avaliacao(self, request, pk=None):
        chamado = self.get_object()
        data = request.data.copy()
        data['chamado'] = chamado.id
        serializer = FechamentoAvaliacaoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Marca o chamado como fechado
        chamado.status = ChamadoStatus.FECHADO
        chamado.resolvido_em = timezone.now()
        chamado.save()

        return Response({
            "avaliacao": serializer.data,
            "chamado": ChamadoDetailSerializer(chamado).data,
        }, status=status.HTTP_201_CREATED)


# =============================================
# Timer (mantém lógica existente)
# =============================================
class ChamadoTimerViewSet(viewsets.ViewSet):

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        chamado = Chamado.objects.get(pk=pk)
        timer, created = ChamadoTimer.objects.get_or_create(
            chamado=chamado, atendente=request.user
        )
        if timer.estado == ChamadoTimerEstado.RODANDO:
            return Response({"message": "Timer ja esta rodando."}, status=status.HTTP_400_BAD_REQUEST)

        timer.estado = ChamadoTimerEstado.RODANDO
        timer.iniciado_em = timezone.now()
        timer.save()
        return Response(ChamadoTimerSerializer(timer).data)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        try:
            timer = ChamadoTimer.objects.get(chamado_id=pk, atendente=request.user)
        except ChamadoTimer.DoesNotExist:
            return Response({"error": "Timer nao encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if timer.estado == ChamadoTimerEstado.PAUSADO:
            return Response({"message": "Timer ja esta pausado."}, status=status.HTTP_400_BAD_REQUEST)

        if timer.iniciado_em:
            delta = timezone.now() - timer.iniciado_em
            timer.tempo_acumulado_segundos += int(delta.total_seconds())

        timer.estado = ChamadoTimerEstado.PAUSADO
        timer.iniciado_em = None
        timer.save()
        return Response(ChamadoTimerSerializer(timer).data)

    @action(detail=True, methods=['post'])
    def finalizar_apontamento(self, request, pk=None):
        descricao = request.data.get('descricao', 'Apontamento automático do timer.')

        try:
            timer = ChamadoTimer.objects.get(chamado_id=pk, atendente=request.user)
        except ChamadoTimer.DoesNotExist:
            return Response({"error": "Timer nao encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if timer.estado == ChamadoTimerEstado.RODANDO and timer.iniciado_em:
            delta = timezone.now() - timer.iniciado_em
            timer.tempo_acumulado_segundos += int(delta.total_seconds())

        total_segundos = timer.tempo_acumulado_segundos
        if total_segundos < 60:
            return Response({"error": "Tempo acumulado insuficiente (< 1 min)."}, status=status.HTTP_400_BAD_REQUEST)

        horas_decimais = round(total_segundos / 3600.0, 2)

        apontamento = ChamadoApontamento.objects.create(
            chamado_id=pk,
            atendente=request.user,
            data=datetime.date.today(),
            horas=horas_decimais,
            descricao=descricao
        )

        timer.tempo_acumulado_segundos = 0
        timer.estado = ChamadoTimerEstado.PAUSADO
        timer.iniciado_em = None
        timer.save()

        return Response({
            "message": "Apontamento gerado com sucesso.",
            "apontamento": ChamadoApontamentoSerializer(apontamento).data,
            "timer": ChamadoTimerSerializer(timer).data
        })


# =============================================
# Cidade
# =============================================
class CidadeViewSet(viewsets.ModelViewSet):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['nome', 'estado']
    ordering_fields = ['nome', 'estado']
    ordering = ['nome']


# =============================================
# Empresa
# =============================================
class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.select_related('cidade').all()
    serializer_class = EmpresaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ativo', 'cidade']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']
    ordering = ['razao_social']


# =============================================
# Cliente Helpdesk
# =============================================
class ClienteHelpdeskViewSet(viewsets.ModelViewSet):
    queryset = ClienteHelpdesk.objects.select_related('cidade', 'empresa').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ativo', 'pendencia_financeira', 'cidade', 'empresa']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'cpf', 'email']
    ordering = ['razao_social']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteHelpdeskListSerializer
        return ClienteHelpdeskSerializer


# =============================================
# Departamento
# =============================================
class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


# =============================================
# Filial
# =============================================
class FilialViewSet(viewsets.ModelViewSet):
    queryset = Filial.objects.select_related('cidade', 'cliente').all()
    serializer_class = FilialSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'cliente', 'cidade']
    search_fields = ['nome']


# =============================================
# Usuário Helpdesk
# =============================================
class UsuarioHelpdeskViewSet(viewsets.ModelViewSet):
    queryset = UsuarioHelpdesk.objects.select_related('user', 'departamento', 'filial', 'cliente').all()
    serializer_class = UsuarioHelpdeskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'perfil', 'departamento', 'filial', 'cliente']
    search_fields = ['nome', 'email', 'login']


# =============================================
# Contrato Helpdesk
# =============================================
class ContratoHelpdeskViewSet(viewsets.ModelViewSet):
    queryset = ContratoHelpdesk.objects.select_related('cliente', 'fornecedor').prefetch_related('anexos').all()
    serializer_class = ContratoHelpdeskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'cliente', 'fornecedor']
    search_fields = ['numero', 'descricao']

    @action(detail=True, methods=['get'])
    def anexos(self, request, pk=None):
        contrato = self.get_object()
        serializer = AnexoContratoSerializer(contrato.anexos.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_anexo(self, request, pk=None):
        contrato = self.get_object()
        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({"error": "Arquivo obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        anexo = AnexoContrato.objects.create(
            contrato=contrato,
            arquivo=arquivo,
            nome_original=arquivo.name,
            tamanho_bytes=arquivo.size,
            mime_type=arquivo.content_type,
        )
        return Response(AnexoContratoSerializer(anexo).data, status=status.HTTP_201_CREATED)


# =============================================
# Atendente
# =============================================
class AtendenteViewSet(viewsets.ModelViewSet):
    queryset = Atendente.objects.select_related('user').all()
    serializer_class = AtendenteSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'email']


# =============================================
# Atividade de Chamado
# =============================================
class AtividadeChamadoViewSet(viewsets.ModelViewSet):
    queryset = AtividadeChamado.objects.select_related('chamado', 'atendente', 'usuario').all()
    serializer_class = AtividadeChamadoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['chamado', 'tipo_atividade', 'publico', 'atendente']
    search_fields = ['descricao']
    ordering = ['-criado_em']


# =============================================
# Anexo de Chamado
# =============================================
class AnexoChamadoViewSet(viewsets.ModelViewSet):
    queryset = AnexoChamado.objects.all()
    serializer_class = AnexoChamadoSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['chamado']


# =============================================
# Catálogo ViewSets
# =============================================
class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'categoria_pai']
    search_fields = ['nome']
    pagination_class = None


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.select_related('categoria').all()
    serializer_class = ServicoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'categoria']
    search_fields = ['nome']
    pagination_class = None


class PrioridadeHelpdeskViewSet(viewsets.ModelViewSet):
    queryset = PrioridadeHelpdesk.objects.all()
    serializer_class = PrioridadeHelpdeskSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class StatusChamadoConfigViewSet(viewsets.ModelViewSet):
    queryset = StatusChamadoConfig.objects.all()
    serializer_class = StatusChamadoConfigSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'eh_fechamento']
    search_fields = ['nome']
    pagination_class = None


class TipoChamadoViewSet(viewsets.ModelViewSet):
    queryset = TipoChamado.objects.all()
    serializer_class = TipoChamadoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class GrupoSolucaoViewSet(viewsets.ModelViewSet):
    queryset = GrupoSolucao.objects.all()
    serializer_class = GrupoSolucaoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class ImpactoViewSet(viewsets.ModelViewSet):
    queryset = Impacto.objects.all()
    serializer_class = ImpactoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class TemaTemplateViewSet(viewsets.ModelViewSet):
    queryset = TemaTemplate.objects.all()
    serializer_class = TemaTemplateSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']
    pagination_class = None


class TemplateChamadoViewSet(viewsets.ModelViewSet):
    queryset = TemplateChamado.objects.select_related('categoria', 'servico', 'tipo', 'tema').all()
    serializer_class = TemplateChamadoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'categoria', 'servico', 'tipo', 'tema']
    search_fields = ['nome']


# =============================================
# Item de Configuração
# =============================================
class ItemConfiguracaoViewSet(viewsets.ModelViewSet):
    queryset = ItemConfiguracao.objects.select_related('cliente', 'filial', 'departamento') \
                                      .prefetch_related('valores_customizados').all()
    serializer_class = ItemConfiguracaoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'tipo', 'cliente', 'filial', 'departamento']
    search_fields = ['nome', 'numero_serie', 'marca', 'modelo']


class CampoCustomizavelICViewSet(viewsets.ModelViewSet):
    queryset = CampoCustomizavelIC.objects.all()
    serializer_class = CampoCustomizavelICSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'tipo_campo', 'obrigatorio']
    search_fields = ['nome']
    pagination_class = None


# =============================================
# Fornecedor
# =============================================
class FornecedorViewSet(viewsets.ModelViewSet):
    queryset = Fornecedor.objects.select_related('cidade', 'area').all()
    serializer_class = FornecedorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'area']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'email']


# =============================================
# Centro de Custo
# =============================================
class CentroCustoViewSet(viewsets.ModelViewSet):
    queryset = CentroCusto.objects.all()
    serializer_class = CentroCustoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome', 'codigo']
    pagination_class = None


# =============================================
# FAQ (Base de Conhecimento)
# =============================================
class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.prefetch_related('anexos').all()
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo', 'categoria']
    search_fields = ['titulo', 'conteudo', 'palavras_chave']

    @action(detail=True, methods=['get'])
    def anexos(self, request, pk=None):
        faq = self.get_object()
        serializer = AnexoFAQSerializer(faq.anexos.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_anexo(self, request, pk=None):
        faq = self.get_object()
        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({"error": "Arquivo obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        anexo = AnexoFAQ.objects.create(
            faq=faq,
            arquivo=arquivo,
            nome_original=arquivo.name,
            tamanho_bytes=arquivo.size,
        )
        return Response(AnexoFAQSerializer(anexo).data, status=status.HTTP_201_CREATED)


# =============================================
# Ligação
# =============================================
class LigacaoViewSet(viewsets.ModelViewSet):
    queryset = Ligacao.objects.select_related('chamado').all()
    serializer_class = LigacaoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['chamado', 'tipo']
    ordering = ['-data']


# =============================================
# Pesquisa de Satisfação
# =============================================
class PesquisaSatisfacaoViewSet(viewsets.ModelViewSet):
    queryset = PesquisaSatisfacao.objects.select_related('chamado').all()
    serializer_class = PesquisaSatisfacaoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['chamado', 'nota']


# =============================================
# Contestação de Chamado
# =============================================
class ContestacaoChamadoViewSet(viewsets.ModelViewSet):
    queryset = ContestacaoChamado.objects.select_related('chamado').all()
    serializer_class = ContestacaoChamadoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['chamado']


# =============================================
# Fechamento com Avaliação
# =============================================
class FechamentoAvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = FechamentoAvaliacao.objects.select_related('chamado').all()
    serializer_class = FechamentoAvaliacaoSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['chamado']


# =============================================
# Formulário de Aprovação
# =============================================
class FormularioAprovacaoViewSet(viewsets.ModelViewSet):
    queryset = FormularioAprovacao.objects.prefetch_related('campos').all()
    serializer_class = FormularioAprovacaoSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['ativo']
    search_fields = ['nome']

    @action(detail=True, methods=['get'])
    def campos(self, request, pk=None):
        formulario = self.get_object()
        serializer = CampoFormularioSerializer(formulario.campos.all(), many=True)
        return Response(serializer.data)


# =============================================
# Configuração de Anexo
# =============================================
class ConfiguracaoAnexoViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracaoAnexo.objects.all()
    serializer_class = ConfiguracaoAnexoSerializer
    pagination_class = None
