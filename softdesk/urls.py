from django.urls import path
from .views import (
    SoftdeskChamadoAPIView,
    SoftdeskImportarAPIView,
    SoftdeskChamadoListAPIView
)

urlpatterns = [
    path("chamado/", SoftdeskChamadoAPIView.as_view()),
    path("importar/", SoftdeskImportarAPIView.as_view()),
    path("chamados/", SoftdeskChamadoListAPIView.as_view()),
]