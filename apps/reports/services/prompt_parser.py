"""
Parser de Prompts para Reportes Dinámicos

Interpreta comandos en lenguaje natural para generar reportes.
Ejemplos:
- "Reporte de ventas de septiembre en PDF"
- "Productos más vendidos del último mes en Excel"
- "Pedidos pendientes en CSV"
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PromptParseError(Exception):
    """Excepción cuando no se puede parsear el prompt"""
    pass


class PromptParser:
    """
    Parser de prompts en lenguaje natural para generación de reportes.
    """

    # Tipos de reportes soportados
    REPORT_TYPES = {
        'ventas': ['ventas', 'venta', 'pedidos', 'pedido', 'ordenes', 'orden'],
        'productos': ['productos', 'producto', 'prendas', 'prenda', 'inventario', 'stock'],
        'clientes': ['clientes', 'cliente', 'usuarios', 'usuario'],
        'analytics': ['analytics', 'anal\u00edticas', 'estad\u00edsticas', 'estadisticas', 'resumen'],
    }

    # Formatos soportados
    FORMATS = ['pdf', 'excel', 'xlsx', 'csv']

    # Períodos de tiempo
    PERIODS = {
        'hoy': 'today',
        'ayer': 'yesterday',
        'esta semana': 'this_week',
        'semana': 'this_week',
        'este mes': 'this_month',
        'mes': 'this_month',
        'último mes': 'last_month',
        'ultimo mes': 'last_month',
        'este año': 'this_year',
        'año': 'this_year',
        'a\u00f1o': 'this_year',
    }

    # Meses en español
    MONTHS = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'setiembre': 9, 'octubre': 10,
        'noviembre': 11, 'diciembre': 12
    }

    # Estados de pedidos
    ORDER_STATUSES = {
        'pendiente': 'pendiente',
        'pendientes': 'pendiente',
        'confirmado': 'confirmado',
        'confirmados': 'confirmado',
        'enviado': 'enviado',
        'enviados': 'enviado',
        'entregado': 'entregado',
        'entregados': 'entregado',
        'cancelado': 'cancelado',
        'cancelados': 'cancelado',
    }

    @classmethod
    def parse(cls, prompt: str) -> Dict[str, Any]:
        """
        Parsear un prompt y extraer la configuración del reporte.

        Args:
            prompt: Texto del prompt en lenguaje natural

        Returns:
            dict: Configuración del reporte {
                'type': str,
                'format': str,
                'period': dict or None,
                'filters': dict,
                'group_by': list,
                'limit': int or None
            }

        Raises:
            PromptParseError: Si el prompt no es válido
        """
        prompt = prompt.lower().strip()

        logger.info(f"Parseando prompt: {prompt}")

        # Extraer tipo de reporte
        report_type = cls._extract_report_type(prompt)

        # Extraer formato
        format_type = cls._extract_format(prompt)

        # Extraer período de tiempo
        period = cls._extract_period(prompt)

        # Extraer filtros adicionales
        filters = cls._extract_filters(prompt, report_type)

        # Extraer agrupación
        group_by = cls._extract_grouping(prompt)

        # Extraer límite
        limit = cls._extract_limit(prompt)

        config = {
            'type': report_type,
            'format': format_type,
            'period': period,
            'filters': filters,
            'group_by': group_by,
            'limit': limit
        }

        logger.info(f"Configuración parseada: {config}")

        return config

    @classmethod
    def _extract_report_type(cls, prompt: str) -> str:
        """Extraer tipo de reporte del prompt"""
        for report_type, keywords in cls.REPORT_TYPES.items():
            for keyword in keywords:
                if keyword in prompt:
                    return report_type

        raise PromptParseError(
            f"No se pudo identificar el tipo de reporte. "
            f"Tipos válidos: {list(cls.REPORT_TYPES.keys())}"
        )

    @classmethod
    def _extract_format(cls, prompt: str) -> str:
        """Extraer formato del reporte"""
        for format_type in cls.FORMATS:
            if format_type in prompt:
                # Normalizar excel/xlsx a 'excel'
                return 'excel' if format_type in ['xlsx', 'excel'] else format_type

        # Por defecto PDF
        return 'pdf'

    @classmethod
    def _extract_period(cls, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Extraer período de tiempo del prompt.

        Returns:
            dict: {'start_date': date, 'end_date': date, 'label': str} o None
        """
        today = datetime.now().date()

        # Buscar períodos predefinidos
        for spanish_period, period_key in cls.PERIODS.items():
            if spanish_period in prompt:
                return cls._get_period_dates(period_key, today)

        # Buscar meses específicos
        for month_name, month_num in cls.MONTHS.items():
            if month_name in prompt:
                # Extraer año si está presente
                year_match = re.search(r'(\d{4})', prompt)
                year = int(year_match.group(1)) if year_match else today.year

                # Primer y último día del mes
                from calendar import monthrange
                start_date = datetime(year, month_num, 1).date()
                _, last_day = monthrange(year, month_num)
                end_date = datetime(year, month_num, last_day).date()

                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': f"{month_name.title()} {year}"
                }

        # Buscar "últimos N días/semanas/meses"
        last_n_match = re.search(r'últimos?\s+(\d+)\s+(d[ií]as?|semanas?|meses?)', prompt)
        if last_n_match:
            quantity = int(last_n_match.group(1))
            unit = last_n_match.group(2)

            if 'd' in unit:  # días
                start_date = today - timedelta(days=quantity)
                label = f"Últimos {quantity} días"
            elif 'semana' in unit:
                start_date = today - timedelta(weeks=quantity)
                label = f"Últimas {quantity} semanas"
            elif 'mes' in unit:
                start_date = today - timedelta(days=quantity * 30)
                label = f"Últimos {quantity} meses"
            else:
                start_date = today

            return {
                'start_date': start_date,
                'end_date': today,
                'label': label
            }

        # Buscar fechas específicas en formato DD/MM/YYYY o YYYY-MM-DD
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        dates = re.findall(date_pattern, prompt)

        if len(dates) >= 2:
            start_date = cls._parse_date(dates[0])
            end_date = cls._parse_date(dates[1])
            return {
                'start_date': start_date,
                'end_date': end_date,
                'label': f"{start_date} a {end_date}"
            }
        elif len(dates) == 1:
            date = cls._parse_date(dates[0])
            return {
                'start_date': date,
                'end_date': date,
                'label': str(date)
            }

        return None

    @classmethod
    def _get_period_dates(cls, period_key: str, today: datetime.date) -> Dict[str, Any]:
        """Obtener fechas para un período predefinido"""
        if period_key == 'today':
            return {
                'start_date': today,
                'end_date': today,
                'label': 'Hoy'
            }
        elif period_key == 'yesterday':
            yesterday = today - timedelta(days=1)
            return {
                'start_date': yesterday,
                'end_date': yesterday,
                'label': 'Ayer'
            }
        elif period_key == 'this_week':
            start = today - timedelta(days=today.weekday())
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Esta semana'
            }
        elif period_key == 'this_month':
            start = today.replace(day=1)
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Este mes'
            }
        elif period_key == 'last_month':
            first_this_month = today.replace(day=1)
            last_month_end = first_this_month - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)
            return {
                'start_date': last_month_start,
                'end_date': last_month_end,
                'label': 'Último mes'
            }
        elif period_key == 'this_year':
            start = today.replace(month=1, day=1)
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Este año'
            }

        return None

    @classmethod
    def _parse_date(cls, date_str: str) -> datetime.date:
        """Parsear string de fecha a objeto date"""
        # Intentar formato DD/MM/YYYY
        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise PromptParseError(f"Formato de fecha no reconocido: {date_str}")

    @classmethod
    def _extract_filters(cls, prompt: str, report_type: str) -> Dict[str, Any]:
        """Extraer filtros adicionales del prompt"""
        filters = {}

        # Si es reporte de ventas/pedidos, buscar estados
        if report_type == 'ventas':
            for status_name, status_value in cls.ORDER_STATUSES.items():
                if status_name in prompt:
                    filters['estado'] = status_value
                    break

        # Buscar "categoría X"
        category_match = re.search(r'categor[ií]a\s+(\w+)', prompt)
        if category_match:
            filters['categoria'] = category_match.group(1).title()

        # Buscar "marca X"
        brand_match = re.search(r'marca\s+(\w+)', prompt)
        if brand_match:
            filters['marca'] = brand_match.group(1).title()

        return filters

    @classmethod
    def _extract_grouping(cls, prompt: str) -> list:
        """Extraer criterios de agrupación"""
        group_by = []

        if 'agrupado por producto' in prompt or 'por producto' in prompt:
            group_by.append('producto')
        if 'agrupado por categor' in prompt or 'por categor' in prompt:
            group_by.append('categoria')
        if 'agrupado por cliente' in prompt or 'por cliente' in prompt:
            group_by.append('cliente')
        if 'agrupado por mes' in prompt or 'por mes' in prompt:
            group_by.append('mes')

        return group_by

    @classmethod
    def _extract_limit(cls, prompt: str) -> Optional[int]:
        """Extraer límite de resultados"""
        # Buscar "top N" o "primeros N"
        top_match = re.search(r'(?:top|primeros?)\s+(\d+)', prompt)
        if top_match:
            return int(top_match.group(1))

        return None
