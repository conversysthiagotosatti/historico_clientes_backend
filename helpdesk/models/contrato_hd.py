from django.db import models


class ContratoHelpdesk(models.Model):
    """
    Contrato no contexto Helpdesk (equivalente ao Contrato no Softdesk).
    """
    numero = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    descricao = models.TextField(blank=True, null=True)

    cliente = models.ForeignKey(
        "helpdesk.ClienteHelpdesk", on_delete=models.CASCADE,
        related_name="contratos_helpdesk", null=True, blank=True
    )

    fornecedor = models.ForeignKey(
        "helpdesk.Fornecedor", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contratos_helpdesk"
    )

    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    horas_previstas = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contrato Helpdesk"
        verbose_name_plural = "Contratos Helpdesk"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Contrato {self.numero or self.id}"


class AnexoContrato(models.Model):
    contrato = models.ForeignKey(
        ContratoHelpdesk, on_delete=models.CASCADE,
        related_name="anexos"
    )
    arquivo = models.FileField(upload_to="helpdesk/anexos_contrato/")
    nome_original = models.CharField(max_length=255, blank=True, null=True)
    tamanho_bytes = models.BigIntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=120, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anexo de Contrato"
        verbose_name_plural = "Anexos de Contrato"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome_original or f"Anexo {self.id}"
