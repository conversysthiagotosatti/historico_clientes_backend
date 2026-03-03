from django.db import models


class Filial(models.Model):
    nome = models.CharField(max_length=200)

    endereco = models.CharField(max_length=255, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=15, blank=True, null=True)
    cidade = models.ForeignKey(
        "helpdesk.Cidade", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="filiais"
    )

    telefone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    cliente = models.ForeignKey(
        "helpdesk.ClienteHelpdesk", on_delete=models.CASCADE,
        related_name="filiais", null=True, blank=True
    )

    contato_nome = models.CharField(max_length=200, blank=True, null=True)
    contato_email = models.EmailField(blank=True, null=True)
    contato_telefone = models.CharField(max_length=30, blank=True, null=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiais"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
