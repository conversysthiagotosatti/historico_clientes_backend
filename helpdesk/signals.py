from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Chamado, ChamadoHistorico
from .middleware import get_current_user
from config.services import enviar_email_graph
from notificacoes.models import Notificacao

@receiver(pre_save, sender=Chamado)
def track_chamado_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Chamado.objects.get(pk=instance.pk)
            # We store the old status temporarily on the instance
            instance._old_status = old_instance.status
        except Chamado.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Chamado)
def create_chamado_historico_on_status_change(sender, instance, created, **kwargs):
    user = get_current_user()
    
    if created:
        ChamadoHistorico.objects.create(
            chamado=instance,
            status_anterior=None,
            status_novo=instance.status,
            usuario=user,
            observacao="Chamado criado."
        )
    else:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            ChamadoHistorico.objects.create(
                chamado=instance,
                status_anterior=old_status,
                status_novo=instance.status,
                usuario=user,
                observacao=f"Status alterado de {old_status} para {instance.status}."
            )


@receiver(post_save, sender=Chamado)
def enviar_email_chamado_criado(sender, instance, created, **kwargs):
    """
    Envia email ao atendente quando o chamado for criado.
    """

    if not created:
        return

    # Só prossegue se houver atendente
    if not instance.atendente:
        return

    # ==========================
    # 1) E-mail para o atendente
    # ==========================
    if instance.atendente.email:
        assunto = f"Novo chamado atribuído: {instance.titulo}"

        corpo = f"""
Olá {instance.atendente.first_name or instance.atendente.username},

Um novo chamado foi atribuído a você.

Título: {instance.titulo}
Prioridade: {instance.prioridade}
Status: {instance.status}
SLA: {instance.sla_horas} horas

Descrição:
{instance.descricao}

Solicitante: {instance.solicitante.username}

Acesse o sistema para mais detalhes.
"""

        try:
            enviar_email_graph(
                destinatario=instance.atendente.email,
                assunto=assunto,
                corpo=corpo,
            )
        except Exception as e:
            print("Erro ao enviar email do chamado:", e)

    # ==========================
    # 2) Notificação interna
    # ==========================
    cliente_conversys = None
    if instance.cliente_helpdesk and instance.cliente_helpdesk.cliente_conversys:
        cliente_conversys = instance.cliente_helpdesk.cliente_conversys

    try:
        Notificacao.objects.create(
            usuario=instance.atendente,
            cliente=cliente_conversys,
            tipo="alerta",
            titulo=f"Novo chamado atribuído: #{instance.id} - {instance.titulo}",
            mensagem=(
                f"Um novo chamado foi atribuído a você.\n"
                f"Título: {instance.titulo}\n"
                f"Prioridade: {instance.prioridade}\n"
                f"Status: {instance.status}\n"
                f"SLA: {instance.sla_horas} horas"
            ),
        )
    except Exception as e:
        # Não quebra o fluxo do chamado se falhar a notificação
        print("Erro ao criar notificação do chamado:", e)
