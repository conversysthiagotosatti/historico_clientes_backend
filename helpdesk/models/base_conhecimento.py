from django.db import models


class FAQ(models.Model):
    """
    Base de Conhecimento / FAQ.
    """
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    categoria = models.CharField(max_length=200, blank=True, null=True)
    palavras_chave = models.CharField(max_length=500, blank=True, null=True,
                                      help_text="Palavras-chave separadas por vírgula")

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class AnexoFAQ(models.Model):
    faq = models.ForeignKey(
        FAQ, on_delete=models.CASCADE,
        related_name="anexos"
    )
    arquivo = models.FileField(upload_to="helpdesk/anexos_faq/")
    nome_original = models.CharField(max_length=255, blank=True, null=True)
    tamanho_bytes = models.BigIntegerField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anexo de FAQ"
        verbose_name_plural = "Anexos de FAQ"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome_original or f"Anexo {self.id}"
