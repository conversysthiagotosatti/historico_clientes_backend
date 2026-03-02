import requests
from django.conf import settings


def obter_token():
    url = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/oauth2/v2.0/token"

    data = {
        "client_id": settings.AZURE_CLIENT_ID,
        "client_secret": settings.AZURE_CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def enviar_script_por_email(script_obj, destinatarios):
    token = obter_token()

    url = f"https://graph.microsoft.com/v1.0/users/{settings.AZURE_SENDER_EMAIL}/sendMail"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    corpo_email = {
        "message": {
            "subject": f"Script - {script_obj.unidade.hostname}",
            "body": {
                "contentType": "Text",
                "content": f"""
Segue script gerado:

Hostname: {script_obj.unidade.hostname}
Template: {script_obj.template.nome}

Script:

{script_obj.script}
"""
            },
            "toRecipients": [
                {"emailAddress": {"address": email}}
                for email in destinatarios
            ],
        }
    }

    response = requests.post(url, headers=headers, json=corpo_email)
    response.raise_for_status()

    return True