from django.apps import AppConfig


class ContratosConfig(AppConfig):
    name = "contratos"

    def ready(self):
        # registra os sinais (ex.: notificação ao usuario_responsavel ao criar tarefa)
        import contratos.signals  # noqa: F401
