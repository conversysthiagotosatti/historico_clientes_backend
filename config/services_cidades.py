import requests
from django.db import transaction
from clientes.models import Cidade, UnidadeFederacao, Pais, Cliente
from parametro.services import get_parametro_cliente


@transaction.atomic
def importar_cidades_soft4(cliente_id):
    cliente = Cliente.objects.filter(id=cliente_id).first()

    if not cliente:
        raise Exception("Cliente não encontrado")

    BASE_URL = get_parametro_cliente(str(cliente_id), "SOFTDESK_BASE_URL")
    API_KEY = get_parametro_cliente(str(cliente_id), "SOFTDESK_HASH_API")
    API_DESTINO = get_parametro_cliente(str(cliente_id), "SOFTDESK_CIDADE")
    API_URL = F"{BASE_URL}{API_DESTINO}"
    print(API_URL)
    headers = {
        "hash-api": API_KEY
    }

    response = requests.get(API_URL, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Erro ao consumir API: {response.text}")

    data = response.json()

    if "objeto" not in data:
        raise Exception("Resposta inválida da API")

    pais, _ = Pais.objects.get_or_create(
        abreviatura="BRA",
        defaults={"nome": "Brasil"}
    )

    criadas = 0
    atualizadas = 0

    for item in data["objeto"]:
        nome_cidade = item["nome"]
        sigla_uf = item["uf"]

        uf, _ = UnidadeFederacao.objects.get_or_create(
            sigla=sigla_uf,
            defaults={
                "nome": sigla_uf,
                "pais": pais
            }
        )

        cidade, created = Cidade.objects.update_or_create(
            nome=nome_cidade,
            uf=uf,
            defaults={
                "codigo_ibge": item.get("codigo")
            }
        )

        if created:
            criadas += 1
        else:
            atualizadas += 1

    return {
        "total": len(data["objeto"]),
        "criadas": criadas,
        "atualizadas": atualizadas
    }