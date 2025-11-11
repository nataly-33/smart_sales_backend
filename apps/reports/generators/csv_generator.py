"""
Generador de Reportes en CSV

Genera archivos CSV simples con datos tabulares.
"""

import csv
from io import StringIO
from .base import BaseReportGenerator
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CSVReportGenerator(BaseReportGenerator):
    """Generador de reportes en CSV"""

    def __init__(self, title="Reporte", format_type="csv", user=None):
        super().__init__(title, format_type)
        self.rows = []
        self.headers = []
        self.user = user

    def add_section(self, title: str, content: str) -> None:
        """
        Implementar método abstracto: Agregar una sección al reporte.

        Args:
            title: Título de la sección
            content: Contenido de la sección
        """
        # CSV es simple, solo agregaremos como fila de comentario
        self.rows.append([f"# {title}: {content}"])

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
        self.headers = ['#'] + headers

        # Agregar datos como filas con enumeración
        for idx, row in enumerate(data, start=1):
            row_data = [str(idx)] + [str(row.get(col, '')) for col in headers]
            self.rows.append(row_data)

    def generate(self) -> bytes:
        """
        Implementar método abstracto: Generar el CSV y retornar bytes.

        Returns:
            bytes: Contenido del CSV en formato correcto
        """
        output = StringIO()
        writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Escribir encabezados
        if self.headers:
            writer.writerow(self.headers)

        # Escribir filas
        for row in self.rows:
            writer.writerow(row)

        # Convertir a bytes con UTF-8 BOM para mejor compatibilidad con Excel
        csv_content = output.getvalue()
        return '\ufeff'.encode('utf-8') + csv_content.encode('utf-8')

    def save(self, filename: str):
        """Guardar el CSV en un archivo"""
        csv_bytes = self.generate()
        with open(filename, 'wb') as f:
            f.write(csv_bytes)
        return filename
