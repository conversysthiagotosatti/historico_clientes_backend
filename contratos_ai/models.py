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

class MemoriaCalculo(models.Model):

    contrato = models.ForeignKey(
        "contratos.Contrato",
        on_delete=models.CASCADE,
        related_name="memorias_calculo",
    )

    gross_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    cost_products = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    additional_costs = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    gross_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    lucro = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    margem_percentual = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Memória de cálculo"
        verbose_name_plural = "Memórias de cálculo"

    def __str__(self) -> str:
        return f"Memória {self.id} - Contrato {self.contrato_id}"


class MemoriaCalculoItem(models.Model):

    TIPOS = (
        ("receita", "Receita"),
        ("custo", "Custo"),
        ("opex", "OPEX"),
    )

    memoria = models.ForeignKey(
        MemoriaCalculo,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    tipo = models.CharField(max_length=20, choices=TIPOS)
    descricao = models.CharField(max_length=255)

    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.descricao