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

    def __init__(self, title="Reporte", format_type="csv"):
        super().__init__(title, format_type)
        self.rows = []
        self.headers = []

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

        self.headers = headers

        # Agregar datos como filas
        for row in data:
            self.rows.append([str(row.get(col, '')) for col in headers])

    def generate(self) -> bytes:
        """
        Implementar método abstracto: Generar el CSV y retornar bytes.

        Returns:
            bytes: Contenido del CSV
        """
        output = StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        if self.headers:
            writer.writerow(self.headers)

        # Escribir filas
        for row in self.rows:
            writer.writerow(row)

        # Convertir a bytes
        return output.getvalue().encode('utf-8')

    def save(self, filename: str):
        """Guardar el CSV en un archivo"""
        csv_bytes = self.generate()
        with open(filename, 'wb') as f:
            f.write(csv_bytes)
        return filename
