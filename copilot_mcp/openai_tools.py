CONTRATOS_TOOLS = [
    {
        "type": "function",
        "name": "contratos_listar",
        "description": "Lista contratos do cliente (para descobrir contrato_id).",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["cliente_id"],
        },
    },
    {
        "type": "function",
        "name": "contratos_get",
        "description": "Obtém detalhes de um contrato e valida se pertence ao cliente.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "contrato_id": {"type": "integer"},
            },
            "required": ["cliente_id", "contrato_id"],
        },
    },
    {
        "type": "function",
        "name": "contratos_arquivos_listar",
        "description": "Lista arquivos anexados ao contrato (para descobrir contrato_arquivo_id).",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "contrato_id": {"type": "integer"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["cliente_id", "contrato_id"],
        },
    },
    {
        "type": "function",
        "name": "contratos_extrair_clausulas",
        "description": "Extrai cláusulas do PDF do contrato (ContratoArquivo) e cria ContratoClausula.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "contrato_id": {"type": "integer"},
                "contrato_arquivo_id": {"type": "integer"},
                "sobrescrever": {"type": "boolean", "default": False},
            },
            "required": ["cliente_id", "contrato_id", "contrato_arquivo_id"],
        },
    },
    {
        "type": "function",
        "name": "contratos_gerar_tarefas",
        "description": "Gera tarefas do contrato a partir das cláusulas extraídas.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "contrato_id": {"type": "integer"},
                "apenas_sem_tarefas": {"type": "boolean", "default": True},
            },
            "required": ["cliente_id", "contrato_id"],
        },
    },
]

ZABBIX_TOOLS = [
    {
    "type": "function",
    "name": "zabbix_dashboard_executivo",
    "description": "Dashboard executivo consolidado do cliente com SLA, disponibilidade, incidentes e análise automática.",
    "parameters": {
        "type": "object",
        "properties": {
        "cliente_id": { "type": "integer" },
        "ano": { "type": "integer" },
        "mes": { "type": "integer" }
        },
        "required": ["cliente_id", "ano", "mes"]
    }
    },
    {
        "type": "function",
        "name": "zabbix_relatorio_incidentes",
        "description": "Retorna relatório de incidentes por período.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "dias": {"type": "integer", "default": 30},
            },
            "required": ["cliente_id"],
        },
    },
    {
        "type": "function",
        "name": "zabbix_top_hosts_problemas",
        "description": "Lista os hosts com maior número de eventos no período.",
        "parameters": {
            "type": "object",
            "properties": {
                "cliente_id": {"type": "integer"},
                "horas": {"type": "integer", "default": 24},
            },
            "required": ["cliente_id"],
        },
    },
]

TOOLS = CONTRATOS_TOOLS + ZABBIX_TOOLS

OPENAI_TO_INTERNAL = {
    "contratos_listar": "contratos.listar",
    "contratos_get": "contratos.get",
    "contratos_arquivos_listar": "contratos.arquivos_listar",
    "contratos_extrair_clausulas": "contratos.extrair_clausulas",
    "contratos_gerar_tarefas": "contratos.gerar_tarefas",
    "zabbix_dashboard_executivo": "zabbix.dashboard_executivo",
    "zabbix_relatorio_incidentes": "zabbix.relatorio_incidentes",
    "zabbix_top_hosts_problemas": "zabbix.top_hosts_problemas",
}