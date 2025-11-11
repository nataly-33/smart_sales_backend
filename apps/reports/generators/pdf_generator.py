"""
Generador de Reportes en PDF

Utiliza ReportLab para generar PDFs con tablas, texto y estilos personalizados.
"""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from .base import BaseReportGenerator
from typing import List, Dict, Any, Optional
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFReportGenerator(BaseReportGenerator):
    """Generador de reportes en PDF usando ReportLab"""

    def __init__(self, title="Reporte", format_type="pdf", user=None):
        super().__init__(title, format_type)
        self.buffer = BytesIO()
        self.page_number = 1
        self.user = user  # Usuario que genera el reporte
        
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,  # Espacio para logo y header
            bottomMargin=40,
        )
        self.styles = getSampleStyleSheet()
        self.story = []

        # Estilos personalizados con fuentes y colores actualizados
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,  # Más pequeño
            fontName='Times-Bold',  # Times New Roman Bold
            textColor=colors.HexColor('#6d322a'),  # primary-darker
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=11,
            fontName='Times-Bold',
            textColor=colors.HexColor('#6d3222'),  # accent-chocolate
            spaceAfter=4,
            spaceBefore=6,
        ))
        
        self.styles.add(ParagraphStyle(
            name='MetadataStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',  # Helvetica en lugar de Arial (fuente estándar de ReportLab)
            textColor=colors.HexColor('#6d3222'),
            spaceAfter=3,
            leftIndent=0,
        ))

    def add_logo_and_header(self):
        """Agregar logo en esquina superior izquierda"""
        # Buscar logo en frontend/public/logo
        frontend_path = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / 'ss_frontend' / 'public' / 'logo' / 'ss_logo_letra.png'
        
        if frontend_path.exists():
            try:
                logo = Image(str(frontend_path), width=1.2*inch, height=0.4*inch)
                logo.hAlign = 'LEFT'
                self.story.append(logo)
                self.story.append(Spacer(1, 0.1*inch))
            except Exception as e:
                logger.warning(f"No se pudo cargar el logo: {e}")
        
    def add_title(self, title=None):
        """Agregar título al reporte (reducido)"""
        title_text = title or self.title
        self.story.append(Paragraph(title_text, self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.05*inch))

    def add_metadata(self, tenant_name="SmartSales365", generated_by=None, generated_at=None, rol=None, email=None):
        """Agregar metadata completa del reporte"""
        if not generated_at:
            generated_at = datetime.now()
        
        # Extraer información del usuario si está disponible
        if self.user:
            generated_by = generated_by or f"{self.user.nombre} {self.user.apellido}"
            rol = rol or (self.user.rol.nombre if hasattr(self.user, 'rol') else "Usuario")
            email = email or self.user.email

        metadata_lines = [
            f"<b>Organización:</b> {tenant_name}",
            f"<b>Generado por:</b> {generated_by or 'Sistema'}",
            f"<b>Fecha:</b> {generated_at.strftime('%d/%m/%Y %H:%M')}",
        ]
        
        if rol:
            metadata_lines.append(f"<b>Rol:</b> {rol}")
        if email:
            metadata_lines.append(f"<b>Email:</b> {email}")
        
        metadata = "<br/>".join(metadata_lines)
        self.story.append(Paragraph(metadata, self.styles['MetadataStyle']))
        self.story.append(Spacer(1, 0.15*inch))

    def add_heading(self, text):
        """Agregar encabezado de sección"""
        self.story.append(Paragraph(text, self.styles['CustomHeading']))
        self.story.append(Spacer(1, 0.05*inch))

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
        style = ParagraphStyle(
            name='CustomParagraph',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
        )
        self.story.append(Paragraph(text, style))
        self.story.append(Spacer(1, 0.05*inch))

    def add_table(self, data: List[Dict[str, Any]], headers: Optional[List[str]] = None) -> None:
        """
        Implementar método abstracto: Agregar una tabla al reporte con enumeración.

        Args:
            data: Lista de diccionarios con los datos
            headers: Lista de encabezados (opcional)
        """
        if not data:
            return

        # Usar headers si están provided, si no extraer del primer diccionario
        if headers is None:
            headers = list(data[0].keys()) if data else []

        # Agregar columna de enumeración
        enum_header = '#'
        headers_with_enum = [enum_header] + headers

        # Convertir datos a tabla (lista de listas) con enumeración
        table_data = [headers_with_enum]
        for idx, row in enumerate(data, start=1):
            row_data = [str(idx)] + [str(row.get(col, '')) for col in headers]
            table_data.append(row_data)

        # Crear y estilar la tabla con colores rose/cream
        table = Table(table_data)
        table.setStyle(TableStyle([
            # Header con color rose (#cfa195)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cfa195')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Columna # centrada
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            # Datos con fuente Helvetica 9pt
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            # Alternar colores: blanco y cream (#e2b8ad)
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e2b8ad')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a59383')),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.15*inch))

    def add_spacer(self, height=0.1):
        """Agregar espacio vertical (reducido)"""
        self.story.append(Spacer(1, height*inch))

    def add_page_break(self):
        """Agregar salto de página"""
        self.story.append(PageBreak())
    
    def _add_page_number(self, canvas, doc):
        """Callback para agregar número de página en cada hoja"""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6d3222'))
        page_num_text = f"Página {doc.page}"
        canvas.drawRightString(A4[0] - 40, 25, page_num_text)
        canvas.restoreState()

    def generate(self) -> bytes:
        """
        Implementar método abstracto: Generar el PDF y retornar bytes.

        Returns:
            bytes: Contenido del PDF
        """
        # Agregar logo y header al inicio
        self.add_logo_and_header()
        
        # Construir PDF con numeración de páginas
        self.doc.build(self.story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
        self.buffer.seek(0)
        return self.buffer.getvalue()

    def save(self, filename):
        """Guardar el PDF en un archivo"""
        pdf_bytes = self.generate()
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        return filename
