LEGAL_TOPICS = {
    "vigencia_prazo": ["vigência", "prazo", "início", "término", "renovação", "vencimento", "duracao", "período"],
    "rescisao": ["rescisão", "rescindir", "denúncia", "encerramento", "distrato", "resolucao"],
    "multa_penalidade": ["multa", "penalidade", "sanção", "cláusula penal", "indenização", "juros"],
    "pagamento": ["pagamento", "preço", "valor", "faturamento", "nota fiscal", "reajuste"],
    "sla": ["sla", "nível de serviço", "disponibilidade", "atendimento", "incidente", "prazo de resposta"],
    "confidencialidade": ["confidencialidade", "sigilo", "nda", "informações confidenciais"],
    "lgpd": ["lgpd", "dados pessoais", "controlador", "operador", "tratamento", "privacy"],
    "escopo": ["escopo", "objeto", "serviços", "entrega", "responsabilidades", "obrigações", "deveres"],
}

def detect_topics(text: str) -> set[str]:
    t = (text or "").lower()
    found = set()
    for topic, terms in LEGAL_TOPICS.items():
        if any(term in t for term in terms):
            found.add(topic)
    return found
