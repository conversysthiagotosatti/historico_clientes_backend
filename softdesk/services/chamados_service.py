from .client import SoftdeskClient
from parametro.services import get_parametro_cliente


class ChamadoService:

    @staticmethod
    def buscar_por_codigo(cliente_id: int, codigo: int):

        endpoint = get_parametro_cliente(
            str(cliente_id),
            "SOFTDESK_CHAMADO_ID"
        )

        if not endpoint:
            raise Exception("SOFTDESK_CHAMADO_ID não configurado")

        client = SoftdeskClient(cliente_id)

        return client.get(
            endpoint,
            params={"codigo": codigo}
        )