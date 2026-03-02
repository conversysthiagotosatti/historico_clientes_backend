from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Chamado, ChamadoHistorico
from .middleware import get_current_user

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
