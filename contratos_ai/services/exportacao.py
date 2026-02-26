from __future__ import annotations
import os
from django.conf import settings
from django.utils import timezone

from docx import Document
from docx.shared import Pt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from contratos.models import Contrato  # ou o model correto do seu "documento"
from django.shortcuts import get_object_or_404

from contratos_ai.models import DocumentoGerado

from reportlab.lib.pagesizes import A4
from reportlab.lib import utils as rl_utils


def exportar_contrato_word(documento: DocumentoGerado) -> str:
    """
    Exporta contrato para DOCX.
    Retorna caminho do arquivo salvo.
    """

    pasta = os.path.join(settings.MEDIA_ROOT, "contratos")
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"contrato_{documento.id}_{timezone.now().timestamp()}.docx"
    caminho = os.path.join(pasta, nome_arquivo)

    doc = Document()

    for linha in documento.conteudo.split("\n"):
        p = doc.add_paragraph(linha)
        p.style.font.size = Pt(12)

    doc.save(caminho)

    return caminho

def exportar_contrato_pdf(documento: DocumentoGerado) -> str:
    """
    Exporta contrato para PDF.
    Retorna caminho do arquivo salvo.
    """

    pasta = os.path.join(settings.MEDIA_ROOT, "contratos")
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"contrato_{documento.id}_{timezone.now().timestamp()}.pdf"
    caminho = os.path.join(pasta, nome_arquivo)

    doc = SimpleDocTemplate(caminho)
    styles = getSampleStyleSheet()
    elements = []

    for linha in documento.conteudo.split("\n"):
        elements.append(Paragraph(linha, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)

    return caminho

def exportar_contrato(documento_id: int, formato: str = "pdf") -> str:
    """
    Exporta contrato em pdf ou docx.
    """

    documento = DocumentoGerado.objects.get(id=documento_id)

    if formato == "pdf":
        return exportar_contrato_pdf(documento)

    if formato in ["doc", "docx", "word"]:
        return exportar_contrato_word(documento)

    raise Exception("Formato inválido. Use 'pdf' ou 'docx'.")


def _safe(text: str) -> str:
    """
    ReportLab Paragraph interpreta tags tipo <b>. Se o texto vier com <, >, &,
    precisamos escapar pra não quebrar/parsir indevidamente.
    """
    if text is None:
        return ""
    return rl_utils.escapeTextOnce(str(text))


def exportar_contrato_pdf_completo(documento_id: int) -> str:
    """
    Exporta um DocumentoGerado (tipo=contrato) para PDF.
    Retorna o caminho do arquivo gerado.
    """
    documento = get_object_or_404(DocumentoGerado, id=documento_id)

    if documento.tipo != "contrato":
        raise ValueError(f"DocumentoGerado {documento.id} não é do tipo 'contrato' (tipo atual: {documento.tipo}).")

    # pasta de saída
    pasta = os.path.join(settings.MEDIA_ROOT, "contratos_ai")
    os.makedirs(pasta, exist_ok=True)

    nome_arquivo = f"documento_{documento.id}_v{documento.versao}_{documento.tipo}.pdf"
    caminho = os.path.join(pasta, nome_arquivo)

    # PDF
    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=48,
        bottomMargin=48,
        title=f"Contrato - {documento.cliente.nome}",
    )
    styles = getSampleStyleSheet()
    elements = []

    # =====================
    # CAPA
    # =====================
    elements.append(Paragraph("<b>DOCUMENTO GERADO</b>", styles["Title"]))
    elements.append(Spacer(1, 0.25 * inch))

    elements.append(Paragraph(f"<b>Tipo:</b> {_safe(documento.get_tipo_display())}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Cliente:</b> {_safe(documento.cliente.nome)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Versão:</b> {_safe(documento.versao)}", styles["Normal"]))

    dt = documento.criado_em.astimezone(timezone.get_current_timezone()) if documento.criado_em else timezone.now()
    elements.append(Paragraph(f"<b>Criado em:</b> {_safe(dt.strftime('%d/%m/%Y %H:%M'))}", styles["Normal"]))

    if documento.criado_por_id:
        elements.append(Paragraph(f"<b>Criado por:</b> {_safe(str(documento.criado_por))}", styles["Normal"]))

    elements.append(Spacer(1, 0.35 * inch))
    elements.append(Paragraph("Histórico de Clientes — Exportação em PDF", styles["Italic"]))
    elements.append(PageBreak())

    # =====================
    # CONTEÚDO (Markdown “simples” -> PDF)
    # =====================
    elements.append(Paragraph("<b>Conteúdo</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    conteudo = (documento.conteudo or "").strip()
    if not conteudo:
        elements.append(Paragraph("Documento sem conteúdo.", styles["Normal"]))
    else:
        # Render “simples” de markdown -> PDF:
        # - Mantém quebras de linha
        # - Interpreta títulos (#, ##, ###) como Heading
        for raw_line in conteudo.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                elements.append(Spacer(1, 0.12 * inch))
                continue

            # headings markdown
            if line.startswith("### "):
                elements.append(Paragraph(f"<b>{_safe(line[4:])}</b>", styles["Heading3"]))
                elements.append(Spacer(1, 0.08 * inch))
                continue
            if line.startswith("## "):
                elements.append(Paragraph(f"<b>{_safe(line[3:])}</b>", styles["Heading2"]))
                elements.append(Spacer(1, 0.10 * inch))
                continue
            if line.startswith("# "):
                elements.append(Paragraph(f"<b>{_safe(line[2:])}</b>", styles["Heading1"]))
                elements.append(Spacer(1, 0.12 * inch))
                continue

            # listas simples
            if line.lstrip().startswith(("- ", "* ")):
                bullet = line.lstrip()[2:].strip()
                elements.append(Paragraph(f"• {_safe(bullet)}", styles["Normal"]))
                continue

            # parágrafo normal
            elements.append(Paragraph(_safe(line), styles["Normal"]))
            elements.append(Spacer(1, 0.08 * inch))

    elements.append(PageBreak())

    # =====================
    # CONTRACAPA / METADADOS
    # =====================
    elements.append(Paragraph("<b>Metadados e Auditoria</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Este documento foi gerado automaticamente pelo sistema Histórico de Clientes.", styles["Normal"]))
    elements.append(Paragraph("Documento controlado e versionado eletronicamente.", styles["Normal"]))

    #if documento.prompt_usado:
    #elements.append(Spacer(1, 0.2 * inch))
    #    elements.append(Paragraph("<b>Prompt usado (resumo):</b>", styles["Normal"]))
        # não colocar prompt gigante sem limite
    #    prompt_preview = (documento.prompt_usado or "").strip()
    #    if len(prompt_preview) > 1500:
    #        prompt_preview = prompt_preview[:1500] + "..."
    #    elements.append(Paragraph(_safe(prompt_preview).replace("\n", "<br/>"), styles["Code"]))

    doc.build(elements)
    return caminho
