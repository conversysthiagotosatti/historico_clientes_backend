from django.db import models


class CentroCusto(models.Model):
    nome = models.CharField(max_length=200)
    codigo = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    descricao = models.TextField(blank=True, null=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Centro de Custo"
        verbose_name_plural = "Centros de Custo"
        ordering = ["nome"]

    def __str__(self):
        if self.codigo:
            return f"{self.codigo} - {self.nome}"
        return self.nome
