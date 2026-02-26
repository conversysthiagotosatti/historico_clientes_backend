from datetime import datetime
from ..services.sla_service import get_sla_summary
from ..services.availability_service import get_availability_summary
from ..services.event_service import get_event_summary
from ..services.mttr_service import get_mttr
from ..ai.executive_summary import gerar_resumo_executivo


def zabbix_dashboard_executivo(cliente_id: int, ano: int, mes: int) -> dict:
    print(f"Gerando dashboard executivo para cliente_id={cliente_id}, ano={ano}, mes={mes}")
    # 1️⃣ SLA
    sla = get_sla_summary(cliente_id, ano, mes)
    print(f"SLA summary: {sla}")
    # 2️⃣ Disponibilidade
    #disponibilidade = get_availability_summary(cliente_id, ano, mes)
    #print(f"Disponibilidade summary: {disponibilidade}")
    # 3️⃣ Eventos
    #eventos = get_event_summary(cliente_id, ano, mes)
    #print(f"Eventos summary: {eventos}")
    # 4️⃣ MTTR
    #mttr = get_mttr(cliente_id, ano, mes)
    #print(f"MTTR: {mttr} minutos")
    # 5️⃣ Consolidação
    dashboard = {
        "cliente_id": cliente_id,
        "periodo": f"{mes}/{ano}",
        "sla_geral": sla["sla_geral"],
        #"disponibilidade_media": disponibilidade["media"],
        #"total_incidentes": eventos["total"],
        #"eventos_criticos": eventos["criticos"],
        #"mttr_medio_minutos": mttr,
        #"top_hosts_criticos": eventos["top_hosts"],
    }
    print(f"Dashboard executivo gerado: {dashboard}")
    # 6️⃣ Geração de Resumo com IA
    resumo = gerar_resumo_executivo(dashboard)
    print(f"Resumo executivo gerado pela IA: {resumo}")
    dashboard["resumo_executivo"] = resumo

    return dashboard