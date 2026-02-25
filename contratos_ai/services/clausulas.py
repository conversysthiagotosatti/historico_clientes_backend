from ..models import ClausulaBase

def buscar_clausulas_por_contexto(tipo_documento, contexto_texto):
    contexto_texto = contexto_texto.lower()

    clausulas = ClausulaBase.objects.filter(
        ativa=True
    )

    selecionadas = []

    for clausula in clausulas:
        score = 0

        # 1️⃣ peso por tipo
        if tipo_documento in clausula.tipo:
            score += 3

        # 2️⃣ match por palavras-chave
        for palavra in clausula.lista_keywords():
            if palavra in contexto_texto:
                score += 2

        if score > 0:
            selecionadas.append((score, clausula))

    # Ordena por score
    selecionadas.sort(key=lambda x: x[0], reverse=True)

    # Retorna top 5
    return [c[1] for c in selecionadas[:5]]