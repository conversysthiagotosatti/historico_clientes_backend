# accounts/models_equipes.py
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Equipe(models.Model):
    nome = models.CharField(max_length=120)
    descricao = models.TextField(blank=True, null=True)

    # liga a projetos (Contrato como "projeto")
    contratos = models.ManyToManyField("contratos.Contrato", related_name="equipes", blank=True)

    # líder e gerente
    lider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipes_como_lider",
    )
    gerente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipes_como_gerente",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["nome"])]

    def clean(self):
        """
        IMPORTANTE: não valide membros aqui no ADD do admin,
        porque ainda não há PK e os inlines não foram salvos.
        A validação correta fica no admin.save_related().
        """
        return

    def __str__(self):
        return self.nome


class EquipeMembro(models.Model):
    class Papel(models.TextChoices):
        MEMBRO = "MEMBRO", "Membro"
        LIDER = "LIDER", "Líder"
        GERENTE = "GERENTE", "Gerente"

    equipe = models.ForeignKey("accounts.Equipe", on_delete=models.CASCADE, related_name="membros")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="equipes_membro")

    papel = models.CharField(max_length=20, choices=Papel.choices, default=Papel.MEMBRO)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("equipe", "user")]
        indexes = [
            models.Index(fields=["equipe", "papel"]),
            models.Index(fields=["user", "ativo"]),
        ]

    def __str__(self):
        return f"{self.equipe_id} - {self.user_id} ({self.papel})"
