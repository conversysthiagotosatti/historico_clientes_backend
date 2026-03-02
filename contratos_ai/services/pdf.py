from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def gerar_pdf(texto, caminho):
    doc = SimpleDocTemplate(caminho)
    styles = getSampleStyleSheet()
    elements = []

    for linha in texto.split("\n"):
        elements.append(Paragraph(linha, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)