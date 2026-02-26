from django.db import models
from django.contrib.auth import get_user_model
from clientes.models import Cliente

User = get_user_model()


class Notificacao(models.Model):
    TIPO = [
        ("contrato", "Contrato"),
        ("proposta", "Proposta"),
        ("alerta", "Alerta"),
        ("sistema", "Sistema"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notificacoes"
    )

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    tipo = models.CharField(max_length=50, choices=TIPO)
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()

    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"