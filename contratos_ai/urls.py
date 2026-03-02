from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ClausulaBaseViewSet,
    DocumentoGeradoViewSet,
    ExportarContratoAPIView,
    GerarClausulaAPIView,
    GerarContratoAPIView,
)

router = DefaultRouter()
router.register(r"clausulas", ClausulaBaseViewSet)
router.register(r"documentos", DocumentoGeradoViewSet)
urlpatterns = router.urls

urlpatterns += [
    path("gerar-clausula/", GerarClausulaAPIView.as_view()),
    path("gerar-contrato/", GerarContratoAPIView.as_view()),
    path("exportar-contrato/<int:documento_id>/", ExportarContratoAPIView.as_view()),
]