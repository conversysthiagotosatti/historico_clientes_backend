from django.db import models


class ClienteHelpdesk(models.Model):
    """
    Cliente dentro do contexto Helpdesk (equivalente ao Cliente no Softdesk).
    Diferente do clientes.Cliente que é o cliente Conversys.
    """
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    cpf = models.CharField(max_length=15, blank=True, null=True, db_index=True)

    endereco = models.CharField(max_length=255, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=15, blank=True, null=True)
    cidade = models.ForeignKey(
        "helpdesk.Cidade", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="clientes_helpdesk"
    )

    telefone = models.CharField(max_length=30, blank=True, null=True)
    celular = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    empresa = models.ForeignKey(
        "helpdesk.Empresa", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="clientes"
    )

    contato_nome = models.CharField(max_length=200, blank=True, null=True)
    contato_email = models.EmailField(blank=True, null=True)
    contato_telefone = models.CharField(max_length=30, blank=True, null=True)

    pendencia_financeira = models.BooleanField(default=False)
    observacao = models.TextField(blank=True, null=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    # Link opcional ao Cliente Conversys
    cliente_conversys = models.ForeignKey(
        "clientes.Cliente", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="perfis_helpdesk"
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente Helpdesk"
        verbose_name_plural = "Clientes Helpdesk"
        ordering = ["razao_social"]

    def __str__(self):
        return self.nome_fantasia or self.razao_social
