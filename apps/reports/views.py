"""
Vistas para la API de Reportes

Proporciona endpoints para:
- Generar reportes desde prompts de texto
- Obtener analytics y estadísticas
- Generar reportes predefinidos
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
import logging

from .serializers import (
    GenerateReportSerializer,
    PredefinedReportSerializer,
    AnalyticsSerializer
)
from .services import (
    AnalyticsService,
    ReportGeneratorService,
    ReportGeneratorServiceError
)

logger = logging.getLogger(__name__)


class ReportsViewSet(viewsets.ViewSet):
    """
    ViewSet para generación de reportes dinámicos y analytics.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generar un reporte a partir de un prompt en lenguaje natural.

        POST /api/reports/generate/
        Body: {
            "prompt": "Reporte de ventas de septiembre en PDF"
        }

        Returns:
            Archivo del reporte en el formato especificado
        """
        serializer = GenerateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prompt = serializer.validated_data['prompt']

        try:
            # Obtener nombre del usuario
            user_name = request.user.nombre_completo

            # Generar reporte
            file_content, filename, mime_type = ReportGeneratorService.generate_from_prompt(
                prompt=prompt,
                user_name=user_name,
                organization_name="SmartSales365"
            )

            # Retornar archivo
            response = HttpResponse(file_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            logger.info(f"Reporte generado exitosamente: {filename} para {user_name}")
            return response

        except ReportGeneratorServiceError as e:
            logger.error(f"Error al generar reporte: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error inesperado al generar reporte: {e}", exc_info=True)
            return Response(
                {'error': 'Error interno al generar el reporte'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def predefined(self, request):
        """
        Generar un reporte predefinido sin usar prompts.

        POST /api/reports/predefined/
        Body: {
            "report_type": "ventas",
            "format": "pdf",
            "filters": {"estado": "confirmado"}
        }

        Returns:
            Archivo del reporte
        """
        serializer = PredefinedReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        report_type = serializer.validated_data['report_type']
        format_type = serializer.validated_data['format']
        filters = serializer.validated_data.get('filters', {})

        try:
            user_name = request.user.nombre_completo

            file_content, filename, mime_type = ReportGeneratorService.generate_predefined_report(
                report_type=report_type,
                format_type=format_type,
                filters=filters,
                user_name=user_name,
                organization_name="SmartSales365"
            )

            response = HttpResponse(file_content, content_type=mime_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response

        except Exception as e:
            logger.error(f"Error al generar reporte predefinido: {e}", exc_info=True)
            return Response(
                {'error': f'Error al generar reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet para analytics y estadísticas del sistema.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Obtener resumen analítico completo.

        GET /api/analytics/overview/?months=12&days=30

        Returns:
            {
                "sales_by_month": [...],
                "products_by_category": [...],
                "activity_by_day": [...],
                "top_selling_products": [...],
                "summary": {...}
            }
        """
        serializer = AnalyticsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        months = serializer.validated_data['months']
        days = serializer.validated_data['days']

        try:
            data = {
                'sales_by_month': AnalyticsService.get_sales_by_month(months),
                'products_by_category': AnalyticsService.get_products_by_category(),
                'activity_by_day': AnalyticsService.get_activity_by_day(days),
                'top_selling_products': AnalyticsService.get_top_selling_products(limit=10),
                'sales_by_status': AnalyticsService.get_sales_by_status(),
                'summary': AnalyticsService.get_summary(),
                'inventory_summary': AnalyticsService.get_inventory_summary(),
                'customer_analytics': AnalyticsService.get_customer_analytics(),
            }

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error en analytics overview: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener analytics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Obtener resumen general del sistema.

        GET /api/analytics/summary/

        Returns:
            {
                "total_orders": 123,
                "orders_this_month": 45,
                "total_sales": 12345.67,
                ...
            }
        """
        try:
            summary = AnalyticsService.get_summary()
            return Response(summary, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al obtener resumen: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener resumen: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def sales(self, request):
        """
        Obtener datos de ventas por mes.

        GET /api/analytics/sales/?months=12

        Returns:
            [
                {"month": "Nov 2024", "total_sales": 1234.56, "order_count": 10},
                ...
            ]
        """
        months = int(request.query_params.get('months', 12))

        try:
            data = AnalyticsService.get_sales_by_month(months)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al obtener ventas: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener ventas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def products(self, request):
        """
        Obtener productos por categoría y más vendidos.

        GET /api/analytics/products/

        Returns:
            {
                "by_category": [...],
                "top_selling": [...]
            }
        """
        try:
            data = {
                'by_category': AnalyticsService.get_products_by_category(),
                'top_selling': AnalyticsService.get_top_selling_products(limit=10),
            }
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al obtener analytics de productos: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener datos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def inventory(self, request):
        """
        Obtener resumen de inventario.

        GET /api/analytics/inventory/

        Returns:
            {
                "total_products": 123,
                "total_stock": 4567,
                "low_stock_items": 12,
                "out_of_stock_items": 3
            }
        """
        try:
            data = AnalyticsService.get_inventory_summary()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al obtener resumen de inventario: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener inventario: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def customers(self, request):
        """
        Obtener analytics de clientes.

        GET /api/analytics/customers/

        Returns:
            {
                "total_customers": 123,
                "customers_with_orders": 45,
                "average_order_value": 123.45,
                ...
            }
        """
        try:
            data = AnalyticsService.get_customer_analytics()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error al obtener analytics de clientes: {e}", exc_info=True)
            return Response(
                {'error': f'Error al obtener datos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
