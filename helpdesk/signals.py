from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Chamado, ChamadoHistorico
from .middleware import get_current_user
from config.services import enviar_email_graph

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

    # Só envia se houver atendente
    if not instance.atendente:
        return

    # Só envia se o atendente tiver email
    if not instance.atendente.email:
        return

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
            corpo=corpo
        )
    except Exception as e:
        print("Erro ao enviar email do chamado:", e)
