import os
from django.conf import settings
from django.utils import timezone

from docx import Document
from docx.shared import Pt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from contratos_ai.models import DocumentoGerado

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