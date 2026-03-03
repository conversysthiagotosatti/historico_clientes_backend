from django.db import models
from django.conf import settings


class Atendente(models.Model):
    """
    Atendente do helpdesk. Pode ser vinculado a um User do Django.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="perfil_atendente"
    )
    nome = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Atendente"
        verbose_name_plural = "Atendentes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
