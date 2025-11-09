"""
Generador de Reportes en PDF

Utiliza ReportLab para generar PDFs con tablas, texto y estilos personalizados.
"""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from .base import BaseReportGenerator
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator(BaseReportGenerator):
    """Generador de reportes en PDF usando ReportLab"""

    def __init__(self, title="Reporte", format_type="pdf"):
        super().__init__(title, format_type)
        self.buffer = BytesIO()
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        self.styles = getSampleStyleSheet()
        self.story = []

        # Estilos personalizados
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
        ))

    def add_title(self, title=None):
        """Agregar título al reporte"""
        title_text = title or self.title
        self.story.append(Paragraph(title_text, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.2*inch))

    def add_metadata(self, tenant_name, generated_by, generated_at=None):
        """Agregar metadata del reporte"""
        if not generated_at:
            generated_at = datetime.now()

        metadata = f"""
        <b>Organización:</b> {tenant_name}<br/>
        <b>Generado por:</b> {generated_by}<br/>
        <b>Fecha:</b> {generated_at.strftime('%d/%m/%Y %H:%M')}
        """
        self.story.append(Paragraph(metadata, self.styles['Normal']))
        self.story.append(Spacer(1, 0.3*inch))

    def add_heading(self, text):
        """Agregar encabezado de sección"""
        self.story.append(Paragraph(text, self.styles['CustomHeading']))
        self.story.append(Spacer(1, 0.1*inch))

    def add_section(self, title: str, content: str) -> None:
        """
        Implementar método abstracto: Agregar una sección al reporte.

        Args:
            title: Título de la sección
            content: Contenido de la sección
        """
        self.add_heading(title)
        self.add_paragraph(content)

    def add_paragraph(self, text):
        """Agregar párrafo"""
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1*inch))

    def add_table(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> None:
        """
        Implementar método abstracto: Agregar una tabla al reporte.

        Args:
            data: Lista de diccionarios con los datos
            headers: Lista de encabezados (opcional)
        """
        if not data:
            return

        # Usar headers si están provided, si no extraer del primer diccionario
        if headers is None:
            headers = list(data[0].keys()) if data else []

        # Convertir datos a tabla (lista de listas)
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(col, '')) for col in headers])

        # Crear y estilar la tabla
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))

    def add_spacer(self, height=0.2):
        """Agregar espacio vertical"""
        self.story.append(Spacer(1, height*inch))

    def add_page_break(self):
        """Agregar salto de página"""
        self.story.append(PageBreak())

    def generate(self) -> bytes:
        """
        Implementar método abstracto: Generar el PDF y retornar bytes.

        Returns:
            bytes: Contenido del PDF
        """
        self.doc.build(self.story)
        self.buffer.seek(0)
        return self.buffer.getvalue()

    def save(self, filename):
        """Guardar el PDF en un archivo"""
        pdf_bytes = self.generate()
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        return filename
