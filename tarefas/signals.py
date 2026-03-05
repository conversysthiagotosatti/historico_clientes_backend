from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from tarefas.models import Tarefa
from notificacoes.models import Notificacao


User = get_user_model()


@receiver(post_save, sender=Tarefa)
def criar_notificacao_tarefa_criada(sender, instance: Tarefa, created: bool, **kwargs):
    """
    Ao criar uma tarefa, gera notificações para usuários administradores.
    """
    if not created:
        return

    contrato = instance.contrato
    cliente = getattr(contrato, "cliente", None)

    admins = User.objects.filter(is_superuser=True)
    if not admins.exists():
        return

    titulo = f"Nova tarefa criada: {instance.titulo}"
    mensagem = (
        f"Uma nova tarefa foi criada para o contrato '{contrato.titulo}'.\n"
        f"Tarefa: {instance.titulo}\n"
        f"Status: {instance.status}\n"
        f"Horas previstas: {instance.horas_previstas}"
    )

    notificacoes = [
        Notificacao(
            usuario=admin,
            cliente=cliente,
            tipo="sistema",
            titulo=titulo,
            mensagem=mensagem,
        )
        for admin in admins
    ]

    Notificacao.objects.bulk_create(notificacoes)

