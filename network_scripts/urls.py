from django.urls import path
from .views import GerarScriptView, TestarTokenGraphView, TestarEnvioEmailView

urlpatterns = [
    path("gerar/", GerarScriptView.as_view(), name="gerar-script"),
    path("testar-token/", TestarTokenGraphView.as_view()),
    path("testar-email/", TestarEnvioEmailView.as_view()),
]