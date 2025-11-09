"""
Servicio Coordinador de Generación de Reportes

Este servicio coordina todo el proceso de generación de reportes:
1. Parsear el prompt
2. Construir el query
3. Obtener los datos
4. Generar el reporte en el formato deseado
"""

from io import BytesIO
from typing import Dict, Any, Tuple
import logging

from .prompt_parser import PromptParser, PromptParseError
from .query_builder import QueryBuilder, QueryBuilderError
from ..generators import ReportGeneratorFactory

logger = logging.getLogger(__name__)


class ReportGeneratorServiceError(Exception):
    """Excepción para errores en generación de reportes"""
    pass


class ReportGeneratorService:
    """
    Servicio principal para generar reportes dinámicos.
    """

    @classmethod
    def generate_from_prompt(
        cls,
        prompt: str,
        user_name: str = "Sistema",
        organization_name: str = "SmartSales365"
    ) -> Tuple[bytes, str, str]:
        """
        Generar un reporte a partir de un prompt en lenguaje natural.

        Args:
            prompt: Comando en lenguaje natural
            user_name: Nombre del usuario que genera el reporte
            organization_name: Nombre de la organización

        Returns:
            tuple: (contenido_archivo, nombre_archivo, mime_type)

        Raises:
            ReportGeneratorServiceError: Si hay un error en la generación
        """
        try:
            # 1. Parsear el prompt
            logger.info(f"Generando reporte desde prompt: {prompt}")
            config = PromptParser.parse(prompt)

            # 2. Construir query y obtener datos
            result = QueryBuilder.build(config)
            data = result['data']
            metadata = result['metadata']

            # 3. Generar reporte en el formato especificado
            format_type = config['format']
            report_title = cls._generate_title(config)

            if config['type'] == 'analytics' and isinstance(data, dict):
                # Para analytics, generar reporte especial
                file_content, filename, mime_type = cls._generate_analytics_report(
                    data,
                    metadata,
                    format_type,
                    user_name,
                    organization_name
                )
            else:
                # Para otros reportes, generar tabla estándar
                file_content, filename, mime_type = cls._generate_standard_report(
                    data,
                    metadata,
                    report_title,
                    format_type,
                    user_name,
                    organization_name
                )

            logger.info(f"Reporte generado exitosamente: {filename}")
            return file_content, filename, mime_type

        except PromptParseError as e:
            logger.error(f"Error al parsear prompt: {e}")
            raise ReportGeneratorServiceError(f"No se pudo interpretar el prompt: {e}")
        except QueryBuilderError as e:
            logger.error(f"Error al construir query: {e}")
            raise ReportGeneratorServiceError(f"Error al obtener datos: {e}")
        except Exception as e:
            logger.error(f"Error inesperado al generar reporte: {e}", exc_info=True)
            raise ReportGeneratorServiceError(f"Error al generar reporte: {e}")

    @classmethod
    def _generate_title(cls, config: Dict[str, Any]) -> str:
        """Generar título del reporte basado en configuración"""
        type_labels = {
            'ventas': 'Reporte de Ventas',
            'productos': 'Reporte de Productos',
            'clientes': 'Reporte de Clientes',
            'analytics': 'Reporte de Analytics'
        }

        title = type_labels.get(config['type'], 'Reporte')

        if config.get('period'):
            period_label = config['period'].get('label', '')
            if period_label:
                title += f" - {period_label}"

        return title

    @classmethod
    def _generate_standard_report(
        cls,
        data: list,
        metadata: dict,
        title: str,
        format_type: str,
        user_name: str,
        organization_name: str
    ) -> Tuple[bytes, str, str]:
        """Generar reporte estándar con tabla de datos"""
        # Crear generador del tipo especificado
        generator = ReportGeneratorFactory.create(format_type, title=title)

        if format_type == 'pdf':
            # Agregar título y metadata
            generator.add_title(title)
            generator.add_metadata(organization_name, user_name)

            # Agregar información de filtros
            if metadata.get('filters_applied'):
                filters_text = ', '.join([f"{k}: {v}" for k, v in metadata['filters_applied'].items()])
                generator.add_section("Filtros Aplicados", filters_text)

            # Agregar tabla de datos
            if data:
                generator.add_table(data)
            else:
                generator.add_paragraph("No se encontraron datos para los criterios especificados.")

            # Agregar resumen
            generator.add_section("Resumen", f"Total de registros: {metadata.get('total_records', 0)}")

        elif format_type == 'excel':
            # Crear hoja de resumen
            sheet = generator.create_sheet("Resumen")
            generator.add_title_row(sheet, title)

            sheet['A3'] = 'Generado por:'
            sheet['B3'] = user_name
            sheet['A4'] = 'Organización:'
            sheet['B4'] = organization_name
            sheet['A5'] = 'Total de registros:'
            sheet['B5'] = metadata.get('total_records', 0)

            # Crear hoja de datos
            data_sheet = generator.create_sheet("Datos")
            if data:
                generator.add_table(data, start_row=1)

        elif format_type == 'csv':
            # CSV simple con datos
            if data:
                generator.add_table(data)

        # Generar archivo
        file_content = generator.generate()
        filename = generator.get_filename()
        mime_type = generator.get_mime_type()

        return file_content, filename, mime_type

    @classmethod
    def _generate_analytics_report(
        cls,
        data: dict,
        metadata: dict,
        format_type: str,
        user_name: str,
        organization_name: str
    ) -> Tuple[bytes, str, str]:
        """Generar reporte de analytics con múltiples secciones"""
        title = "Reporte de Analytics y Estadísticas"
        generator = ReportGeneratorFactory.create(format_type, title=title)

        if format_type == 'pdf':
            generator.add_title(title)
            generator.add_metadata(organization_name, user_name)

            # Sección: Resumen General
            resumen = data.get('resumen_general', {})
            generator.add_section(
                "Resumen General",
                f"""
                Total de pedidos: {resumen.get('total_orders', 0)}<br/>
                Pedidos este mes: {resumen.get('orders_this_month', 0)}<br/>
                Ventas totales: Bs. {resumen.get('total_sales', 0):.2f}<br/>
                Ventas este mes: Bs. {resumen.get('sales_this_month', 0):.2f}<br/>
                Total productos: {resumen.get('total_products', 0)}<br/>
                Total clientes: {resumen.get('total_customers', 0)}
                """
            )

            # Sección: Productos Más Vendidos
            top_products = data.get('productos_mas_vendidos', [])
            if top_products:
                generator.add_heading("Top 10 Productos Más Vendidos")
                generator.add_table(top_products)

            # Sección: Ventas por Mes
            ventas_mes = data.get('ventas_por_mes', [])
            if ventas_mes:
                generator.add_heading("Ventas por Mes")
                generator.add_table(ventas_mes)

            # Sección: Pedidos por Estado
            pedidos_estado = data.get('pedidos_por_estado', [])
            if pedidos_estado:
                generator.add_heading("Pedidos por Estado")
                generator.add_table(pedidos_estado)

        elif format_type == 'excel':
            # Hoja de resumen
            sheet_resumen = generator.create_sheet("Resumen General")
            generator.add_title_row(sheet_resumen, "Resumen General")

            resumen = data.get('resumen_general', {})
            row = 3
            for key, value in resumen.items():
                sheet_resumen.cell(row=row, column=1, value=key.replace('_', ' ').title())
                sheet_resumen.cell(row=row, column=2, value=value)
                row += 1

            # Hoja de productos más vendidos
            top_products = data.get('productos_mas_vendidos', [])
            if top_products:
                sheet_products = generator.create_sheet("Top Productos")
                generator.add_table(top_products, start_row=1)

            # Hoja de ventas por mes
            ventas_mes = data.get('ventas_por_mes', [])
            if ventas_mes:
                sheet_ventas = generator.create_sheet("Ventas por Mes")
                generator.add_table(ventas_mes, start_row=1)

        elif format_type == 'csv':
            # Para CSV, incluir resumen y productos más vendidos
            resumen = data.get('resumen_general', {})
            generator.add_section("Resumen General", "")

            # Agregar resumen como tabla
            resumen_data = [{'Métrica': k.replace('_', ' ').title(), 'Valor': v} for k, v in resumen.items()]
            generator.add_table(resumen_data)

            # Agregar productos más vendidos
            top_products = data.get('productos_mas_vendidos', [])
            if top_products:
                generator.add_section("Top Productos Más Vendidos", "")
                generator.add_table(top_products)

        # Generar archivo
        file_content = generator.generate()
        filename = generator.get_filename()
        mime_type = generator.get_mime_type()

        return file_content, filename, mime_type

    @classmethod
    def generate_predefined_report(
        cls,
        report_type: str,
        format_type: str = 'pdf',
        filters: dict = None,
        user_name: str = "Sistema",
        organization_name: str = "SmartSales365"
    ) -> Tuple[bytes, str, str]:
        """
        Generar un reporte predefinido sin usar prompts.

        Args:
            report_type: Tipo de reporte ('ventas', 'productos', 'clientes', 'analytics')
            format_type: Formato del reporte ('pdf', 'excel', 'csv')
            filters: Filtros adicionales
            user_name: Nombre del usuario
            organization_name: Nombre de la organización

        Returns:
            tuple: (contenido_archivo, nombre_archivo, mime_type)
        """
        config = {
            'type': report_type,
            'format': format_type,
            'period': None,
            'filters': filters or {},
            'group_by': [],
            'limit': None
        }

        # Construir query y obtener datos
        result = QueryBuilder.build(config)
        data = result['data']
        metadata = result['metadata']

        # Generar reporte
        title = cls._generate_title(config)

        if report_type == 'analytics' and isinstance(data, dict):
            return cls._generate_analytics_report(
                data,
                metadata,
                format_type,
                user_name,
                organization_name
            )
        else:
            return cls._generate_standard_report(
                data,
                metadata,
                title,
                format_type,
                user_name,
                organization_name
            )
