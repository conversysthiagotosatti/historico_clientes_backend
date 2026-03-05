from django.db import models


# =============================================
# Categoria (hierárquica — self-referencing)
# =============================================
class Categoria(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    categoria_pai = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="subcategorias"
    )
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Serviço
# =============================================
class Servico(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="servicos"
    )
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Serviço"
        verbose_name_plural = "Serviços"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Prioridade (configurável, diferente do enum atual)
# =============================================
class PrioridadeHelpdesk(models.Model):
    nome = models.CharField(max_length=100)
    valor = models.IntegerField(default=0, help_text="Valor numérico para ordenação (menor = mais urgente)")
    cor = models.CharField(max_length=20, default="#ff9800")
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prioridade"
        verbose_name_plural = "Prioridades"
        ordering = ["valor"]

    def __str__(self):
        return self.nome


# =============================================
# Status de Chamado (configurável)
# =============================================
class StatusChamadoConfig(models.Model):
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=20, default="#2196f3")
    eh_fechamento = models.BooleanField(default=False,
                                        help_text="Indica se este status fecha o chamado")
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Status de Chamado"
        verbose_name_plural = "Status de Chamado"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Tipo de Chamado
# =============================================
class TipoChamado(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Chamado"
        verbose_name_plural = "Tipos de Chamado"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Área
# =============================================
class Area(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Grupo de Solução
# =============================================
class GrupoSolucao(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Grupo de Solução"
        verbose_name_plural = "Grupos de Solução"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Impacto / Nível de Indisponibilidade
# =============================================
class Impacto(models.Model):
    nome = models.CharField(max_length=200)
    nivel = models.IntegerField(default=0, help_text="Nível numérico do impacto")
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Impacto"
        verbose_name_plural = "Impactos"
        ordering = ["nivel"]

    def __str__(self):
        return self.nome


# =============================================
# Tema de Template
# =============================================
class TemaTemplate(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tema de Template"
        verbose_name_plural = "Temas de Template"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


# =============================================
# Template de Chamado
# =============================================
class TemplateChamado(models.Model):
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="templates"
    )
    servico = models.ForeignKey(
        Servico, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="templates"
    )
    tipo = models.ForeignKey(
        TipoChamado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="templates"
    )
    tema = models.ForeignKey(
        TemaTemplate, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="templates"
    )

    ativo = models.BooleanField(default=True)
    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template de Chamado"
        verbose_name_plural = "Templates de Chamado"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
