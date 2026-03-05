from softdesk.services.client import SoftdeskClient
from parametro.services import get_parametro_cliente


class DepartamentoSoftdeskService:
    """
    Serviço para buscar departamentos na API do Softdesk.

    Espera que exista, para o cliente, um parâmetro
    `SOFTDESK_DEPARTAMENTO_ENDPOINT` contendo o path do endpoint,
    por exemplo: `/api.php/departamento/`.
    """

    @staticmethod
    def listar(cliente_id: int):
        cliente_id_str = str(cliente_id)

        endpoint = get_parametro_cliente(
            cliente_id_str,
            "SOFTDESK_DEPARTAMENTO_ENDPOINT",
        )

        if not endpoint:
            raise Exception("SOFTDESK_DEPARTAMENTO_ENDPOINT não configurado")

        client = SoftdeskClient(cliente_id)
        data = client.get(endpoint)

        # A API costuma retornar algo como:
        # {
        #   "mensagem": "...",
        #   "objeto": [ { ... departamentos ... } ]
        # }
        if isinstance(data, dict):
            return data.get("objeto", []) or []

        # Se já vier como lista, apenas retorna
        return data or []

