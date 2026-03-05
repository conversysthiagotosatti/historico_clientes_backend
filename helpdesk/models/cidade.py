from django.db import models


class Cidade(models.Model):
    nome = models.CharField(max_length=200)
    estado = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, default="Brasil")
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        ordering = ["nome"]

    def __str__(self):
        if self.estado:
            return f"{self.nome} - {self.estado}"
        return self.nome
