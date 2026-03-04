from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChamadoViewSet, ChamadoTimerViewSet,
    CidadeViewSet, EmpresaViewSet, ClienteHelpdeskViewSet,
    DepartamentoViewSet, FilialViewSet, UsuarioHelpdeskViewSet,
    ContratoHelpdeskViewSet, AtendenteViewSet,
    AtividadeChamadoViewSet, AnexoChamadoViewSet,
    CategoriaViewSet, ServicoViewSet, PrioridadeHelpdeskViewSet,
    StatusChamadoConfigViewSet, TipoChamadoViewSet, AreaViewSet,
    GrupoSolucaoViewSet, ImpactoViewSet, TemaTemplateViewSet,
    TemplateChamadoViewSet,
    ItemConfiguracaoViewSet, CampoCustomizavelICViewSet,
    FornecedorViewSet, CentroCustoViewSet,
    FAQViewSet, LigacaoViewSet,
    PesquisaSatisfacaoViewSet, ContestacaoChamadoViewSet,
    FechamentoAvaliacaoViewSet,
    FormularioAprovacaoViewSet, ConfiguracaoAnexoViewSet,
)

router = DefaultRouter()

# Core
router.register(r'chamados', ChamadoViewSet, basename='chamado')

# Cadastro
router.register(r'cidades', CidadeViewSet, basename='cidade')
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'clientes-hd', ClienteHelpdeskViewSet, basename='cliente-hd')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'filiais', FilialViewSet, basename='filial')
router.register(r'usuarios-hd', UsuarioHelpdeskViewSet, basename='usuario-hd')
router.register(r'contratos-hd', ContratoHelpdeskViewSet, basename='contrato-hd')
router.register(r'atendentes', AtendenteViewSet, basename='atendente')

# Catálogo
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'prioridades', PrioridadeHelpdeskViewSet, basename='prioridade')
router.register(r'status-chamado', StatusChamadoConfigViewSet, basename='status-chamado')
router.register(r'tipos-chamado', TipoChamadoViewSet, basename='tipo-chamado')
router.register(r'areas', AreaViewSet, basename='area')
router.register(r'grupos-solucao', GrupoSolucaoViewSet, basename='grupo-solucao')
router.register(r'impactos', ImpactoViewSet, basename='impacto')
router.register(r'temas-template', TemaTemplateViewSet, basename='tema-template')
router.register(r'templates-chamado', TemplateChamadoViewSet, basename='template-chamado')

# Atividades e Anexos (acesso direto)
router.register(r'atividades', AtividadeChamadoViewSet, basename='atividade')
router.register(r'anexos-chamado', AnexoChamadoViewSet, basename='anexo-chamado')

# IC
router.register(r'itens-configuracao', ItemConfiguracaoViewSet, basename='item-configuracao')
router.register(r'campos-ic', CampoCustomizavelICViewSet, basename='campo-ic')

# Outros
router.register(r'fornecedores', FornecedorViewSet, basename='fornecedor')
router.register(r'centros-custo', CentroCustoViewSet, basename='centro-custo')
router.register(r'faq', FAQViewSet, basename='faq')
router.register(r'ligacoes', LigacaoViewSet, basename='ligacao')
router.register(r'pesquisas-satisfacao', PesquisaSatisfacaoViewSet, basename='pesquisa-satisfacao')
router.register(r'contestacoes', ContestacaoChamadoViewSet, basename='contestacao')
router.register(r'fechamentos-avaliacao', FechamentoAvaliacaoViewSet, basename='fechamento-avaliacao')
router.register(r'formularios', FormularioAprovacaoViewSet, basename='formulario')
router.register(r'config-anexo', ConfiguracaoAnexoViewSet, basename='config-anexo')

urlpatterns = [
    path('', include(router.urls)),

    # Custom Timer Actions under /helpdesk/timers/<chamado_id>/<action>/
    path('timers/<int:pk>/start/', ChamadoTimerViewSet.as_view({'post': 'start'}), name='timer-start'),
    path('timers/<int:pk>/pause/', ChamadoTimerViewSet.as_view({'post': 'pause'}), name='timer-pause'),
    path('timers/<int:pk>/finalizar/', ChamadoTimerViewSet.as_view({'post': 'finalizar_apontamento'}), name='timer-finalizar'),
]
