import requests
from django.conf import settings
from django.core.cache import cache


def gerar_token_graph():
    """
    Gera token OAuth2 via Azure AD usando client_credentials.
    Usa cache para evitar requisições desnecessárias.
    """

    token_cache = cache.get("azure_graph_token")

    if token_cache:
        return token_cache

    url = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token"
    
    print(url)
    print(settings.AZURE_CLIENT_ID)
    print(settings.AZURE_CLIENT_SECRET)
    payload = {
        "client_id": settings.AZURE_CLIENT_ID,
        "client_secret": settings.AZURE_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception(f"Erro ao gerar token Azure: {response.text}")

    token_data = response.json()

    # Cache por 55 minutos (token dura 60)
    cache.set("azure_graph_token", token_data, timeout=3300)

    return token_data

def enviar_email_graph(destinatario, assunto, corpo, anexo_nome=None, anexo_conteudo=None):
    """
    Envia email via Microsoft Graph usando Application Permission.
    """

    token_data = gerar_token_graph()
    access_token = token_data["access_token"]
    print(access_token)
    url = f"https://graph.microsoft.com/v1.0/users/{settings.EMAIL_SENDER}/sendMail"

    email_msg = {
        "message": {
            "subject": assunto,
            "body": {
                "contentType": "Text",
                "content": corpo,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": destinatario
                    }
                }
            ],
        },
        "saveToSentItems": "true"
    }

    # Se tiver anexo
    if anexo_nome and anexo_conteudo:
        import base64

        email_msg["message"]["attachments"] = [
            {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": anexo_nome,
                "contentType": "text/plain",
                "contentBytes": base64.b64encode(
                    anexo_conteudo.encode()
                ).decode()
            }
        ]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, headers=headers, json=email_msg)

    if response.status_code not in (202, 200):
        raise Exception(f"Erro ao enviar email: {response.text}")

    return {"status": "Email enviado com sucesso"}