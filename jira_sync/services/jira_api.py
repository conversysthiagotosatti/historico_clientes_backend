import requests
from urllib.parse import urljoin
from parametro.services import get_parametro_cliente, get_sufixo_api_jira, get_prefixo_api_jira


def montar_url_jira(base_url: str, cloud_id: str, sufixo_url: str) -> str:
    """
    Monta a URL final da API do Jira Cloud (OAuth2).
    """
    base = f"{base_url.rstrip('/')}/{cloud_id}/"
    return urljoin(base, sufixo_url.lstrip("/"))



def listar_projetos_jira(access_token: str):
    base_url = get_prefixo_api_jira(1, "PROJ_CLIENTES", default="https://api.atlassian.com/ex/jira") #"https://api.atlassian.com/ex/jira"
    cloud_id = get_parametro_cliente("1", "Jira_Id") #"f57354ee-1d8f-4cbb-90bf-44900ed06ea1"
    sufixo_url = get_sufixo_api_jira(1, "PROJ_CLIENTES", default="/rest/api/3") #"/rest/api/3/project/search"

    url = montar_url_jira(base_url, cloud_id, sufixo_url)

    print(url)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(
            f"Erro Jira {response.status_code}: {response.text}"
        )

    return response.json()
