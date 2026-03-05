from django.db.models.signals import post_save
from django.dispatch import receiver

from contratos.models import ContratoTarefa
from notificacoes.models import Notificacao


@receiver(post_save, sender=ContratoTarefa)
def notificar_usuario_responsavel_tarefa(sender, instance: ContratoTarefa, created: bool, **kwargs):
    """
    Ao criar uma ContratoTarefa, envia uma notificação para o usuario_responsavel (se houver).
    """
    if not created:
        return

    responsavel = instance.usuario_responsavel
    if not responsavel:
        return

    contrato = instance.contrato
    cliente = contrato.cliente if hasattr(contrato, "cliente") else None

    titulo = f"Nova tarefa do contrato: {instance.titulo}"
    mensagem = (
        f"Uma nova tarefa foi atribuída a você.\n"
        f"Contrato: {contrato.titulo}\n"
        f"Tarefa: {instance.titulo}\n"
        f"Status: {instance.status}\n"
        f"Prioridade sugerida: {instance.prioridade or 'N/A'}\n"
        f"Prazo sugerido (dias): {instance.prazo_dias_sugerido or 'N/A'}"
    )

    try:
        Notificacao.objects.create(
            usuario=responsavel,
            cliente=cliente,
            tipo="alerta",
            titulo=titulo,
            mensagem=mensagem,
        )
    except Exception as exc:
        # Não quebra o fluxo da criação de tarefa se falhar a notificação
        print(f"Erro ao criar notificação para usuario_responsavel da tarefa {instance.id}: {exc}")

