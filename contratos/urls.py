from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_pdf import AnalisarContratoPDFView
from .views_copilot import CopilotContratoQueryView
from .views import ContratoViewSet, ContratoTarefaViewSet, ContratoClausulaViewSet
from .views_arquivo import ContratoArquivoViewSet

router = DefaultRouter()
router.register(r"contratos", ContratoViewSet, basename="contratos")
router.register(r"contratos/tarefas", ContratoTarefaViewSet, basename="contrato-tarefas")
router.register(r"contratos/clausulas", ContratoClausulaViewSet, basename="contrato-clausulas")
router.register(r"contratos/arquivos", ContratoArquivoViewSet, basename="contrato-arquivos")

urlpatterns = [
    # ✅ inclui TODAS as rotas do router
    path("", include(router.urls)),

    # rotas customizadas
    path("contratos/<int:pk>/analisar-pdf/", AnalisarContratoPDFView.as_view(), name="analisar-contrato-pdf"),
    path("copilot/contratos/<int:contrato_id>/query/", CopilotContratoQueryView.as_view(), name="copilot-contrato-query"),
]