from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    documento = models.CharField(max_length=30, blank=True, null=True)  # CPF/CNPJ
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    # ✅ Novo campo logotipo
    logotipo = models.ImageField(
        upload_to="clientes/logotipos/",
        blank=True,
        null=True,
        help_text="Imagem do logotipo do cliente (PNG/JPG/SVG)",
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome
