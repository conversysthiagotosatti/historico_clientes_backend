from django.db import models


class ConfiguracaoAnexo(models.Model):
    """
    Configurações globais de anexo (extensões permitidas, tamanho máximo, etc.).
    """
    extensoes_permitidas = models.JSONField(
        default=list,
        help_text="Lista de extensões permitidas, ex: ['pdf', 'jpg', 'png', 'doc']"
    )
    tamanho_max_mb = models.IntegerField(
        default=10,
        help_text="Tamanho máximo em MB por anexo"
    )
    descricao = models.CharField(max_length=200, blank=True, null=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuração de Anexo"
        verbose_name_plural = "Configurações de Anexo"

    def __str__(self):
        return self.descricao or f"Config Anexo #{self.id}"
