from django.db import models


class Empresa(models.Model):
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    inscricao_estadual = models.CharField(max_length=30, blank=True, null=True)
    inscricao_municipal = models.CharField(max_length=30, blank=True, null=True)

    endereco = models.CharField(max_length=255, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=15, blank=True, null=True)
    cidade = models.ForeignKey(
        "helpdesk.Cidade", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="empresas"
    )

    telefone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    site = models.URLField(blank=True, null=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["razao_social"]

    def __str__(self):
        return self.nome_fantasia or self.razao_social
