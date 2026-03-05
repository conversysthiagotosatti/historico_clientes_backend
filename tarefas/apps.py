from django.apps import AppConfig


class TarefasConfig(AppConfig):
    name = "tarefas"

    def ready(self):
        # Importa sinais para garantir registro dos handlers
        import tarefas.signals  # noqa: F401

