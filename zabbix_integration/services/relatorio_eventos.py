import os
from datetime import timedelta
from django.conf import settings
from django.db.models import Q

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape

from zabbix_integration.models import ZabbixEvent, ZabbixHost, ZabbixTrigger


def formatar_duracao(inicio, fim):
    delta = fim - inicio
    total_segundos = int(delta.total_seconds())

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def gerar_relatorio_eventos_recovery(cliente_id: int) -> str:

    eventos_problem = ZabbixEvent.objects.filter(
        cliente_id=cliente_id,
        value=1
    ).exclude(
        Q(r_eventid__isnull=True) | Q(r_eventid="") | Q(r_eventid="0")
    )

    pasta = os.path.join(settings.MEDIA_ROOT, "relatorios")
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(
        pasta,
        f"relatorio_eventos_cliente_{cliente_id}.pdf"
    )

    # 🔥 LANDSCAPE
    doc = SimpleDocTemplate(
        caminho,
        pagesize=landscape(A4)
    )

    elements = []
    styles = getSampleStyleSheet()

    # 🔥 Fonte menor para tabela
    estilo_tabela = ParagraphStyle(
        name="Tabela",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    elements.append(
        Paragraph("Relatório de Eventos com Recovery - Zabbix", styles["Heading1"])
    )
    elements.append(Spacer(1, 0.3 * inch))

    dados_tabela = [[
        "Host",
        "Trigger",
        "Evento Original",
        "Recovery",
        "Duração"
    ]]

    for evento in eventos_problem:

        recovery = ZabbixEvent.objects.filter(
            cliente_id=cliente_id,
            eventid=evento.r_eventid
        ).first()

        if not recovery:
            continue

        duracao = formatar_duracao(evento.clock, recovery.clock)
        #buscar trigger para pegar nome e host
        trigger = ZabbixTrigger.objects.filter(
            cliente_id=cliente_id,
            triggerid=str(evento.objectid)
        ).first()

        host_nome = "-"
        trigger_nome = "-"

        if trigger:
            trigger_nome = trigger.description or trigger.name or "-"
            
            item = trigger.items.first()
            if item and item.host:
                host_nome = item.host.nome

                dados_tabela.append([
                                    Paragraph(host_nome, estilo_tabela),
                                    Paragraph(evento.name or "-", estilo_tabela),
                                    Paragraph(evento.clock.strftime("%d/%m/%Y %H:%M:%S"), estilo_tabela),
                                    Paragraph(recovery.clock.strftime("%d/%m/%Y %H:%M:%S"), estilo_tabela),
                                    Paragraph(duracao, estilo_tabela),
                                ])

    # 🔥 Definindo largura fixa das colunas
    largura_total = 11 * inch  # largura útil landscape A4
    col_widths = [
        2.2 * inch,  # Host
        4.0 * inch,  # Trigger
        1.8 * inch,  # Evento original
        1.8 * inch,  # Recovery
        1.2 * inch,  # Duração
    ]

    tabela = Table(
        dados_tabela,
        colWidths=col_widths,
        repeatRows=1
    )

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    elements.append(tabela)
    doc.build(elements)

    return caminho