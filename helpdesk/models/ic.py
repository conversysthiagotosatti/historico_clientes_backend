from django.db import models


class ItemConfiguracao(models.Model):
    """
    Item de Configuração (IC) — ativo/equipamento gerenciado.
    """
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)

    cliente = models.ForeignKey(
        "helpdesk.ClienteHelpdesk", on_delete=models.CASCADE,
        related_name="itens_configuracao", null=True, blank=True
    )
    filial = models.ForeignKey(
        "helpdesk.Filial", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="itens_configuracao"
    )
    departamento = models.ForeignKey(
        "helpdesk.Departamento", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="itens_configuracao"
    )

    data_aquisicao = models.DateField(null=True, blank=True)
    data_garantia = models.DateField(null=True, blank=True)
    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de Configuração"
        verbose_name_plural = "Itens de Configuração"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.numero_serie or 'S/N'})"


class CampoCustomizavelIC(models.Model):
    """
    Campo customizável para Itens de Configuração.
    """
    class TipoCampo(models.TextChoices):
        TEXTO = "TEXTO", "Texto"
        NUMERO = "NUMERO", "Número"
        DATA = "DATA", "Data"
        LISTA = "LISTA", "Lista"
        BOOLEANO = "BOOLEANO", "Booleano"

    nome = models.CharField(max_length=200)
    tipo_campo = models.CharField(max_length=20, choices=TipoCampo.choices, default=TipoCampo.TEXTO)
    obrigatorio = models.BooleanField(default=False)
    opcoes = models.JSONField(blank=True, null=True, help_text="Opções para tipo LISTA (array de strings)")

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campo Customizável de IC"
        verbose_name_plural = "Campos Customizáveis de IC"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class ValorCampoIC(models.Model):
    """
    Valor de um campo customizável para um IC específico.
    """
    item_configuracao = models.ForeignKey(
        ItemConfiguracao, on_delete=models.CASCADE,
        related_name="valores_customizados"
    )
    campo = models.ForeignKey(
        CampoCustomizavelIC, on_delete=models.CASCADE,
        related_name="valores"
    )
    valor = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Valor de Campo IC"
        verbose_name_plural = "Valores de Campos IC"
        unique_together = ("item_configuracao", "campo")

    def __str__(self):
        return f"{self.campo.nome}: {self.valor}"
