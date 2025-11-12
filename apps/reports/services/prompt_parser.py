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
        'ventas': ['ventas', 'venta', 'pedidos', 'pedido', 'ordenes', 'orden', 'compras', 'compra'],
        'productos': ['productos', 'producto', 'prendas', 'prenda', 'inventario', 'stock'],
        'clientes': ['clientes', 'cliente', 'usuarios', 'usuario', 'compradores'],
        'analytics': ['analytics', 'analíticas', 'estadísticas', 'estadisticas', 'resumen', 'dashboard', 'métricas', 'metricas'],
        'logins': ['logins', 'inicios de sesión', 'sesiones', 'accesos', 'ingresos al sistema'],
        'carritos': ['carritos', 'carritos activos', 'carros de compra'],
        'top_productos': ['top productos', 'productos más vendidos', 'más vendidos', 'best sellers'],
        'ingresos': ['ingresos', 'ganancias', 'facturación', 'facturacion', 'revenue'],
    }

    # Formatos soportados
    FORMATS = ['pdf', 'excel', 'xlsx', 'csv']

    # Períodos de tiempo
    PERIODS = {
        'hoy': 'today',
        'ayer': 'yesterday',
        'esta semana': 'this_week',
        'semana actual': 'this_week',
        'semana pasada': 'last_week',
        'anterior semana': 'last_week',
        'la anterior semana': 'last_week',
        'este mes': 'this_month',
        'mes actual': 'this_month',
        'último mes': 'last_month',
        'ultimo mes': 'last_month',
        'mes pasado': 'last_month',
        'este año': 'this_year',
        'año actual': 'this_year',
        'año 2025': 'year_2025',
        'año 2024': 'year_2024',
        '2025': 'year_2025',
        '2024': 'year_2024',
        # Trimestres
        'primer trimestre': 'q1',
        'trimestre 1': 'q1',
        'q1': 'q1',
        'segundo trimestre': 'q2',
        'trimestre 2': 'q2',
        'q2': 'q2',
        'tercer trimestre': 'q3',
        'trimestre 3': 'q3',
        'q3': 'q3',
        'cuarto trimestre': 'q4',
        'trimestre 4': 'q4',
        'q4': 'q4',
        # Semestres
        'primer semestre': 'h1',
        'semestre 1': 'h1',
        'h1': 'h1',
        'segundo semestre': 'h2',
        'semestre 2': 'h2',
        'h2': 'h2',
        # Períodos relativos
        'últimos 7 días': 'last_7_days',
        'últimos 30 días': 'last_30_days',
        'últimos 90 días': 'last_90_days',
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

        # 1. PRIORIDAD MÁXIMA: Buscar rangos explícitos de fechas PRIMERO
        # "del DD/MM/YYYY al DD/MM/YYYY" tiene máxima prioridad
        range_patterns = [
            r'del?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+al?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'desde\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+hasta\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'entre\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+y\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, prompt)
            if match:
                start_date = cls._parse_date(match.group(1))
                end_date = cls._parse_date(match.group(2))
                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
                }

        # 2. Buscar trimestres con año específico: "primer trimestre 2024"
        quarter_year_patterns = [
            (r'(?:primer|1er|primero)\s+trimestre\s+(\d{4})', 'q1'),
            (r'(?:segundo|2do)\s+trimestre\s+(\d{4})', 'q2'),
            (r'(?:tercer|3er|tercero)\s+trimestre\s+(\d{4})', 'q3'),
            (r'(?:cuarto|4to)\s+trimestre\s+(\d{4})', 'q4'),
            (r'q([1-4])\s+(\d{4})', None),  # "Q1 2024"
        ]
        
        for pattern, quarter in quarter_year_patterns:
            match = re.search(pattern, prompt)
            if match:
                if quarter:
                    year = int(match.group(1))
                    return cls._get_quarter_dates(quarter, year)
                else:
                    # Formato Q1 2024
                    quarter_num = match.group(1)
                    year = int(match.group(2))
                    return cls._get_quarter_dates(f'q{quarter_num}', year)

        # 3. Buscar semestres con año específico: "primer semestre 2024"
        semester_year_patterns = [
            (r'(?:primer|1er|primero)\s+semestre\s+(\d{4})', 'h1'),
            (r'(?:segundo|2do)\s+semestre\s+(\d{4})', 'h2'),
            (r'h([1-2])\s+(\d{4})', None),  # "H1 2024"
        ]
        
        for pattern, semester in semester_year_patterns:
            match = re.search(pattern, prompt)
            if match:
                if semester:
                    year = int(match.group(1))
                    return cls._get_semester_dates(semester, year)
                else:
                    # Formato H1 2024
                    semester_num = match.group(1)
                    year = int(match.group(2))
                    return cls._get_semester_dates(f'h{semester_num}', year)

        # 4. Buscar meses con año específico: "octubre 2025"
        for month_name, month_num in cls.MONTHS.items():
            # Buscar formato "octubre 2025" o "octubre del 2025"
            month_year_pattern = rf'{month_name}\s+(?:del?\s+)?(\d{{4}})'
            match = re.search(month_year_pattern, prompt)
            if match:
                year = int(match.group(1))
                from calendar import monthrange
                start_date = datetime(year, month_num, 1).date()
                _, last_day = monthrange(year, month_num)
                end_date = datetime(year, month_num, last_day).date()

                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': f"{month_name.title()} {year}"
                }

        # 5. Buscar años específicos como "del año 2024", "año 2024", "2024"
        year_patterns = [
            (r'(?:del?\s+)?año\s+(\d{4})', None),  # "del año 2024", "año 2024"
            (r'(?:del?\s+|en\s+)?(\d{4})(?:\s+|$)', None),  # "2024", "del 2024", "en 2024"
        ]
        
        for pattern, _ in year_patterns:
            match = re.search(pattern, prompt)
            if match:
                year = int(match.group(1))
                # Verificar si es un año válido (entre 2020 y 2030)
                if 2020 <= year <= 2030:
                    return {
                        'start_date': datetime(year, 1, 1).date(),
                        'end_date': datetime(year, 12, 31).date(),
                        'label': f'Año {year}'
                    }

        # 6. Buscar períodos predefinidos (esta semana, este mes, etc.)
        for spanish_period, period_key in cls.PERIODS.items():
            if spanish_period in prompt:
                return cls._get_period_dates(period_key, today)

        # 7. Buscar solo meses (sin año = año actual)
        for month_name, month_num in cls.MONTHS.items():
            if month_name in prompt and not re.search(rf'{month_name}\s+\d{{4}}', prompt):
                year = today.year
                from calendar import monthrange
                start_date = datetime(year, month_num, 1).date()
                _, last_day = monthrange(year, month_num)
                end_date = datetime(year, month_num, last_day).date()

                return {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': f"{month_name.title()} {year}"
                }

        # 8. Buscar "últimos N días/semanas/meses"
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

        # 9. Si no encontró rangos explícitos, buscar fechas individuales
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})'
        dates = re.findall(date_pattern, prompt)

        if len(dates) >= 2:
            start_date = cls._parse_date(dates[0])
            end_date = cls._parse_date(dates[1])
            return {
                'start_date': start_date,
                'end_date': end_date,
                'label': f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
            }
        elif len(dates) == 1:
            date = cls._parse_date(dates[0])
            return {
                'start_date': date,
                'end_date': date,
                'label': date.strftime('%d/%m/%Y')
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
        elif period_key == 'last_week':
            # Lunes de la semana pasada
            start = today - timedelta(days=today.weekday() + 7)
            # Domingo de la semana pasada
            end = start + timedelta(days=6)
            return {
                'start_date': start,
                'end_date': end,
                'label': 'Semana pasada'
            }
        elif period_key == 'last_7_days':
            start = today - timedelta(days=7)
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Últimos 7 días'
            }
        elif period_key == 'last_30_days':
            start = today - timedelta(days=30)
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Últimos 30 días'
            }
        elif period_key == 'last_90_days':
            start = today - timedelta(days=90)
            return {
                'start_date': start,
                'end_date': today,
                'label': 'Últimos 90 días'
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
        elif period_key == 'year_2025':
            return {
                'start_date': datetime(2025, 1, 1).date(),
                'end_date': datetime(2025, 12, 31).date(),
                'label': 'Año 2025'
            }
        elif period_key == 'year_2024':
            return {
                'start_date': datetime(2024, 1, 1).date(),
                'end_date': datetime(2024, 12, 31).date(),
                'label': 'Año 2024'
            }
        # Trimestres (año actual por defecto)
        elif period_key in ['q1', 'q2', 'q3', 'q4']:
            return cls._get_quarter_dates(period_key, today.year)
        # Semestres (año actual por defecto)
        elif period_key in ['h1', 'h2']:
            return cls._get_semester_dates(period_key, today.year)

        return None

    @classmethod
    def _get_quarter_dates(cls, quarter: str, year: int) -> Dict[str, Any]:
        """
        Obtener fechas para un trimestre específico.
        Q1: Ene-Mar, Q2: Abr-Jun, Q3: Jul-Sep, Q4: Oct-Dic
        """
        quarters = {
            'q1': (1, 3, 'Primer Trimestre'),
            'q2': (4, 6, 'Segundo Trimestre'),
            'q3': (7, 9, 'Tercer Trimestre'),
            'q4': (10, 12, 'Cuarto Trimestre'),
        }
        
        start_month, end_month, label = quarters[quarter.lower()]
        
        from calendar import monthrange
        _, last_day = monthrange(year, end_month)
        
        return {
            'start_date': datetime(year, start_month, 1).date(),
            'end_date': datetime(year, end_month, last_day).date(),
            'label': f"{label} {year}"
        }

    @classmethod
    def _get_semester_dates(cls, semester: str, year: int) -> Dict[str, Any]:
        """
        Obtener fechas para un semestre específico.
        H1: Ene-Jun, H2: Jul-Dic
        """
        if semester.lower() == 'h1':
            return {
                'start_date': datetime(year, 1, 1).date(),
                'end_date': datetime(year, 6, 30).date(),
                'label': f"Primer Semestre {year}"
            }
        else:  # h2
            return {
                'start_date': datetime(year, 7, 1).date(),
                'end_date': datetime(year, 12, 31).date(),
                'label': f"Segundo Semestre {year}"
            }

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
        """Extraer criterios de agrupación - soporta singular y plural"""
        group_by = []
        
        # Normalizar prompt
        prompt_lower = prompt.lower()

        # Producto/Productos
        if re.search(r'productos?(?:\s|$|,|y)', prompt_lower):
            # Verificar que es contexto de agrupación
            if re.search(r'(?:agrupada?s?|por)\s+(?:\w+\s+)?productos?', prompt_lower):
                group_by.append('producto')
        
        # Categoría/Categorías  
        if re.search(r'categor[ií]as?(?:\s|$|,|y)', prompt_lower):
            if re.search(r'(?:agrupada?s?|por)\s+(?:\w+\s+)?categor[ií]as?', prompt_lower):
                group_by.append('categoria')
        
        # Cliente/Clientes
        if re.search(r'clientes?(?:\s|$|,|y)', prompt_lower):
            if re.search(r'(?:agrupada?s?|por)\s+(?:\w+\s+)?clientes?', prompt_lower):
                group_by.append('cliente')
        
        # Mes/Meses - evitar confusión con fechas
        if re.search(r'meses?(?:\s|$|,|y)', prompt_lower):
            # Buscar en contexto de agrupación, no en fechas
            if re.search(r'(?:agrupada?s?|por)\s+(?:\w+\s+)?meses?', prompt_lower):
                # Excluir casos como "desde el mes de"
                if not re.search(r'(?:desde|del|en el|para el)\s+mes(?:es)?', prompt_lower):
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
