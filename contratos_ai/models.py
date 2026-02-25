from django.db import models
from clientes.models import Cliente
from django.contrib.auth import get_user_model

User = get_user_model()


class ClausulaBase(models.Model):
    TIPO = [
        ("financeiro", "Financeiro"),
        ("sla", "SLA"),
        ("tecnica", "Técnica"),
        ("lgpd", "LGPD"),
        ("penalidade", "Penalidade"),
        ("rescisao", "Rescisão"),
        ("monitoramento", "Monitoramento"),
        ("comercial", "Comercial"),
    ]

    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, choices=TIPO)
    texto = models.TextField()
    palavras_chave = models.CharField(
        max_length=500,
        help_text="Separadas por vírgula"
    )
    ativa = models.BooleanField(default=True)
    versao = models.IntegerField(default=1)
    criada_em = models.DateTimeField(auto_now_add=True)

    def lista_keywords(self):
        return [k.strip().lower() for k in self.palavras_chave.split(",")]
    
class DocumentoGerado(models.Model):
    TIPO = [
        ("contrato", "Contrato"),
        ("proposta_tecnica", "Proposta Técnica"),
        ("proposta_comercial", "Proposta Comercial"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, choices=TIPO)
    prompt_usado = models.TextField()
    conteudo = models.TextField()
    versao = models.IntegerField(default=1)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)