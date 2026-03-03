from django.db import models

class Pais(models.Model):
    nome = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=3)
    
    def __str__(self):
        return self.nome

class UnidadeFederacao(models.Model):
    pais = models.ForeignKey(
        Pais,
        on_delete=models.CASCADE,
        related_name="UF",
    )
    nome = models.CharField(max_length=30)
    sigla = models.CharField(max_length=3)

    def __str__(self):
        return self.nome 

class Cidade(models.Model):
    nome = models.CharField(max_length=200)
    uf = models.ForeignKey(
        UnidadeFederacao,
        on_delete=models.CASCADE,
        related_name="UnidadeFederacao",
    )
    codigo_ibge = models.CharField(max_length = 10, blank=True, null=True)
    codigo_aeroporto = models.CharField(max_length = 5, blank=True, null=True)

    def __str__(self):
        return self.nome


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
    
    codigo_integracao = models.CharField(max_length=20, null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.CASCADE, related_name="Cidade", null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    endereco_numero = models.CharField(max_length=10, null=True, blank=True)
    endereco_compl = models.CharField(max_length=10, null=True, blank=True)
    bairro = models.CharField(max_length=30, null=True, blank=True)
    cep = models.CharField(max_length=100, null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome
