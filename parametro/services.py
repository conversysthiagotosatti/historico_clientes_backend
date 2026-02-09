from parametro.models import ParametroCliente
from jira_sync.models import JiraConnection


def get_parametro_cliente(cliente_id: int, nome_parametro: str, default=None):
    """
    Retorna o valor de um parâmetro de um cliente.

    :param cliente_id: ID do cliente
    :param nome_parametro: Nome do parâmetro
    :param default: Valor retornado se não encontrar
    """
    try:
        return (
            ParametroCliente.objects
            .only("valor")
            .get(cliente_id=cliente_id, nome=nome_parametro)
            .valor
        )
    except ParametroCliente.DoesNotExist:
        return default
    
def get_sufixo_api_jira(cliente_id: int, nome_parametro: str, default=None):
    """
    Retorna o sufixo da api do jira.

    :param cliente_id: ID do cliente
    :param nome_parametro: Nome do parâmetro
    :param default: Valor retornado se não encontrar
    """
    try:
        return (
            JiraConnection.objects
            .only("sufixo_url")
            .get(cliente_id=cliente_id, nome_jira=nome_parametro)
            .sufixo_url
        )
    except JiraConnection.DoesNotExist:
        return default
    
def get_prefixo_api_jira(cliente_id: int, nome_parametro: str, default=None):
    """
    Retorna o prefixo da api do jira.

    :param cliente_id: ID do cliente
    :param nome_parametro: Nome do parâmetro
    :param default: Valor retornado se não encontrar
    """
    try:
        return (
            JiraConnection.objects
            .only("base_url")
            .get(cliente_id=cliente_id, nome_jira=nome_parametro)
            .base_url
        )
    except JiraConnection.DoesNotExist:
        return default
