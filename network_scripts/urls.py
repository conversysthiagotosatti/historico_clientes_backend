from django.urls import path
from .views import GerarScriptView

urlpatterns = [
    path("gerar/", GerarScriptView.as_view(), name="gerar-script"),
]