from django.db import models
from django.conf import settings


class UsuarioHelpdesk(models.Model):
    """
    Perfil estendido de um usuário no contexto Helpdesk.
    Vincula ao auth.User do Django, mas adiciona campos específicos do helpdesk.
    """
    class Perfil(models.TextChoices):
        ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
        ATENDENTE = "ATENDENTE", "Atendente"
        CLIENTE = "CLIENTE", "Cliente"
        SOLICITANTE = "SOLICITANTE", "Solicitante"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="perfil_helpdesk", null=True, blank=True
    )

    nome = models.CharField(max_length=200)
    login = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)

    perfil = models.CharField(max_length=20, choices=Perfil.choices,
                              default=Perfil.SOLICITANTE)

    departamento = models.ForeignKey(
        "helpdesk.Departamento", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="usuarios"
    )
    filial = models.ForeignKey(
        "helpdesk.Filial", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="usuarios"
    )
    cliente = models.ForeignKey(
        "helpdesk.ClienteHelpdesk", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="usuarios"
    )

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True,
                                            help_text="Código original no Softdesk")

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Usuário Helpdesk"
        verbose_name_plural = "Usuários Helpdesk"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
