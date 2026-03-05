from django.db import models


class FormularioAprovacao(models.Model):
    """
    Formulário de aprovação configurável.
    """
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Formulário de Aprovação"
        verbose_name_plural = "Formulários de Aprovação"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class CampoFormulario(models.Model):
    """
    Campo de um formulário de aprovação.
    """
    class TipoCampo(models.TextChoices):
        TEXTO = "TEXTO", "Texto"
        NUMERO = "NUMERO", "Número"
        DATA = "DATA", "Data"
        LISTA = "LISTA", "Lista"
        BOOLEANO = "BOOLEANO", "Booleano"
        TEXTAREA = "TEXTAREA", "Área de Texto"

    formulario = models.ForeignKey(
        FormularioAprovacao, on_delete=models.CASCADE,
        related_name="campos"
    )
    nome = models.CharField(max_length=200)
    tipo_campo = models.CharField(max_length=20, choices=TipoCampo.choices, default=TipoCampo.TEXTO)
    obrigatorio = models.BooleanField(default=False)
    opcoes = models.JSONField(blank=True, null=True, help_text="Opções para tipo LISTA")
    ordem = models.IntegerField(default=0)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Campo de Formulário"
        verbose_name_plural = "Campos de Formulário"
        ordering = ["formulario", "ordem"]

    def __str__(self):
        return f"{self.formulario.nome} - {self.nome}"
