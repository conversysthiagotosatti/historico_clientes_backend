from django.conf import settings
from django.db import models
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models_equipes import Equipe, EquipeMembro

class UserClienteRole(models.TextChoices):
    LIDER = "LIDER", "Líder"
    GERENTE_PROJETO = "GERENTE_PROJETO", "Gerente de Projeto"
    ANALISTA = "ANALISTA", "Analista"


class UserClienteMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=30, choices=UserClienteRole.choices, default=UserClienteRole.ANALISTA)
    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "cliente")
        indexes = [
            models.Index(fields=["user", "ativo"]),
            models.Index(fields=["cliente", "role", "ativo"]),
        ]

    def __str__(self):
        return f"{self.user} -> {self.cliente} ({self.role})"

class MeClientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ms = (
            request.user.memberships
            .filter(ativo=True)
            .select_related("cliente")
            .order_by("cliente__nome")
        )
        return Response([
            {"cliente_id": m.cliente_id, "cliente_nome": m.cliente.nome, "role": m.role}
            for m in ms
        ])

class UserProfile(models.Model):
    class Tipo(models.TextChoices):
        INTERNO = "INTERNO", "Interno"
        CLIENTE = "CLIENTE", "Cliente"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    tipo_usuario = models.CharField(max_length=20, choices=Tipo.choices, default=Tipo.INTERNO)
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def clean(self):
        # regra: se for CLIENTE, tem que ter cliente
        if self.tipo_usuario == self.Tipo.CLIENTE and not self.cliente_id:
            from django.core.exceptions import ValidationError
            raise ValidationError({"cliente": "Usuário do tipo CLIENTE deve estar vinculado a um cliente."})

        # regra: se for INTERNO, cliente deve ser null (opcional mas recomendado)
        if self.tipo_usuario == self.Tipo.INTERNO and self.cliente_id:
            from django.core.exceptions import ValidationError
            raise ValidationError({"cliente": "Usuário INTERNO não deve estar vinculado a cliente."})

class Modulo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class ModuloPermissao(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name="permissoes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="permissoes")
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.CASCADE, related_name="permissoes", null=True, blank=True)
    permissao = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("modulo", "user")

    def __str__(self):
        return f"{self.modulo} - {self.user} - {self.permissao}"