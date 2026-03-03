from django.db import models
from django.conf import settings


class AtividadeChamado(models.Model):
    """
    Atividade/registro de trabalho vinculado a um chamado.
    Equivalente a 'Atividade de Chamado' no Softdesk.
    """
    class TipoAtividade(models.TextChoices):
        INTERNA = "INTERNA", "Interna"
        PUBLICA = "PUBLICA", "Pública"
        REMOTA = "REMOTA", "Remota"
        PRESENCIAL = "PRESENCIAL", "Presencial"
        TELEFONE = "TELEFONE", "Telefone"

    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="atividades"
    )
    descricao = models.TextField()

    tipo_atividade = models.CharField(
        max_length=20, choices=TipoAtividade.choices,
        default=TipoAtividade.PUBLICA
    )

    atendente = models.ForeignKey(
        "helpdesk.Atendente", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="atividades"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="atividades_helpdesk"
    )

    tempo_gasto_minutos = models.IntegerField(default=0)
    publico = models.BooleanField(default=True,
                                  help_text="Se visível para o solicitante/cliente")

    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atividade de Chamado"
        verbose_name_plural = "Atividades de Chamado"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Atividade #{self.id} - Chamado #{self.chamado_id}"
