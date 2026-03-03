from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Setor(models.Model):
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=20, default="#00a651")
    icone = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"

    def __str__(self):
        return self.nome
