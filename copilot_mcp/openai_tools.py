TOOLS = [
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

OPENAI_TO_INTERNAL = {
    "contratos_listar": "contratos.listar",
    "contratos_get": "contratos.get",
    "contratos_arquivos_listar": "contratos.arquivos_listar",
    "contratos_extrair_clausulas": "contratos.extrair_clausulas",
    "contratos_gerar_tarefas": "contratos.gerar_tarefas",
}