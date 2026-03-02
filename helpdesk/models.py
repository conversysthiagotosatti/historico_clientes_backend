from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Setor(models.Model):
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=20, default="#00a651")
    icone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nome

class ChamadoStatus(models.TextChoices):
    ABERTO = "ABERTO", "Aberto"
    EM_ATENDIMENTO = "EM_ATENDIMENTO", "Em Atendimento"
    AGUARDANDO = "AGUARDANDO", "Aguardando"
    RESOLVIDO = "RESOLVIDO", "Resolvido"
    FECHADO = "FECHADO", "Fechado"
    CANCELADO = "CANCELADO", "Cancelado"

class ChamadoPrioridade(models.TextChoices):
    CRITICA = "CRITICA", "Crítica"
    ALTA = "ALTA", "Alta"
    MEDIA = "MEDIA", "Média"
    BAIXA = "BAIXA", "Baixa"

class Chamado(models.Model):
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    setor = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name="chamados")
    
    status = models.CharField(max_length=20, choices=ChamadoStatus.choices, default=ChamadoStatus.ABERTO)
    prioridade = models.CharField(max_length=20, choices=ChamadoPrioridade.choices, default=ChamadoPrioridade.MEDIA)
    
    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name="chamados_solicitados")
    atendente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="chamados_atendidos")
    
    chamados_vinculados = models.ManyToManyField("self", blank=True)
    sla_horas = models.IntegerField(default=48)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    resolvido_em = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"#{self.id} - {self.titulo}"

class ChamadoTipoAutor(models.TextChoices):
    SOLICITANTE = "SOLICITANTE", "Solicitante"
    ATENDENTE = "ATENDENTE", "Atendente"
    SISTEMA = "SISTEMA", "Sistema"

class ChamadoMensagem(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="mensagens")
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_autor = models.CharField(max_length=20, choices=ChamadoTipoAutor.choices)
    conteudo = models.TextField()
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

class ChamadoHistorico(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="historico")
    status_anterior = models.CharField(max_length=20, null=True, blank=True)
    status_novo = models.CharField(max_length=20)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observacao = models.CharField(max_length=255, null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

class ChamadoApontamento(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="apontamentos")
    atendente = models.ForeignKey(User, on_delete=models.PROTECT)
    data = models.DateField()
    horas = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']

class ChamadoTimerEstado(models.TextChoices):
    RODANDO = "RODANDO", "Rodando"
    PAUSADO = "PAUSADO", "Pausado"

class ChamadoTimer(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="timers")
    atendente = models.ForeignKey(User, on_delete=models.CASCADE)
    
    estado = models.CharField(max_length=20, choices=ChamadoTimerEstado.choices, default=ChamadoTimerEstado.PAUSADO)
    iniciado_em = models.DateTimeField(null=True, blank=True)
    tempo_acumulado_segundos = models.IntegerField(default=0)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('chamado', 'atendente')
