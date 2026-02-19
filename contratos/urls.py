from django.urls import path
from .views_pdf import AnalisarContratoPDFView
from .views_copilot import CopilotContratoQueryView

urlpatterns = [
    path("contratos/<int:pk>/analisar-pdf/", AnalisarContratoPDFView.as_view(), name="analisar-contrato-pdf"),
    path("copilot/contratos/<int:contrato_id>/query/", CopilotContratoQueryView.as_view()),
]
