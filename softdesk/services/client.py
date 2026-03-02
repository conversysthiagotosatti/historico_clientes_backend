import requests
from parametro.services import get_parametro_cliente


class SoftdeskClient:

    def __init__(self, cliente_id: int):
        self.cliente_id = str(cliente_id)

        base_url = get_parametro_cliente(self.cliente_id, "SOFTDESK_BASE_URL")
        self.base_url = base_url.rstrip("/") if base_url else None

        hash_api = get_parametro_cliente(self.cliente_id, "SOFTDESK_HASH_API")
        self.hash_api = hash_api.strip() if hash_api else None

        if not self.base_url:
            raise Exception("SOFTDESK_BASE_URL não configurado")

        if not self.hash_api:
            raise Exception("SOFTDESK_HASH_API não configurado")

    def get(self, endpoint: str, params: dict = None):

        url = f"{self.base_url}{endpoint}"

        headers = {
            "Content-Type": "application/json",
            "hash-api": self.hash_api,
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=30
        )

        print(f"Request URL: {response.request.url}")

        if response.status_code != 200:
            raise Exception(f"Softdesk API Error: {response.text}")

        return response.json()