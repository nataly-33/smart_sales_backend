"""
Query Builder Dinámico

Construye queries de Django ORM basados en la configuración del reporte.
"""

from django.db.models import Q, Count, Sum, Avg, F
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QueryBuilderError(Exception):
    """Excepción para errores en construcción de queries"""
    pass


class QueryBuilder:
    """
    Construye queries dinámicamente basados en configuración de reportes.
    """

    @classmethod
    def build(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construir query y obtener datos según configuración.

        Args:
            config: Configuración del reporte (del PromptParser)

        Returns:
            dict: Datos del reporte {
                'data': list,
                'metadata': dict
            }
        """
        report_type = config.get('type')

        if report_type == 'ventas':
            return cls._build_sales_report(config)
        elif report_type == 'productos':
            return cls._build_products_report(config)
        elif report_type == 'clientes':
            return cls._build_customers_report(config)
        elif report_type == 'analytics':
            return cls._build_analytics_report(config)
        elif report_type == 'logins':
            return cls._build_logins_report(config)
        elif report_type == 'carritos':
            return cls._build_carts_report(config)
        elif report_type == 'top_productos':
            return cls._build_top_products_report(config)
        elif report_type == 'ingresos':
            return cls._build_revenue_report(config)
        else:
            raise QueryBuilderError(f"Tipo de reporte no soportado: {report_type}")

    @classmethod
    def _build_sales_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de ventas/pedidos"""
        from apps.orders.models import Pedido, DetallePedido

        # Iniciar queryset
        queryset = Pedido.objects.all()

        # Aplicar filtros de período
        if config.get('period'):
            start_date = config['period']['start_date']
            end_date = config['period']['end_date']
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

        # Aplicar filtros adicionales
        filters = config.get('filters', {})
        if 'estado' in filters:
            queryset = queryset.filter(estado=filters['estado'])

        # Agrupación
        group_by = config.get('group_by', [])

        if 'producto' in group_by:
            # Agrupar por producto (usar DetallePedido)
            detalles_qs = DetallePedido.objects.filter(
                pedido__in=queryset
            ).values(
                'prenda__nombre',
                'prenda__precio'
            ).annotate(
                cantidad_total=Sum('cantidad'),
                total_ventas=Sum(F('cantidad') * F('precio_unitario'))
            ).order_by('-cantidad_total')

            if config.get('limit'):
                detalles_qs = detalles_qs[:config['limit']]

            data = [{
                'producto': item['prenda__nombre'],
                'precio': float(item['prenda__precio']),
                'cantidad_vendida': item['cantidad_total'],
                'total_ventas': float(item['total_ventas'])
            } for item in detalles_qs]

        elif 'mes' in group_by:
            # Agrupar por mes
            ventas_por_mes = queryset.extra({
                'mes': "EXTRACT(month FROM created_at)",
                'anio': "EXTRACT(year FROM created_at)"
            }).values('mes', 'anio').annotate(
                cantidad_pedidos=Count('id'),
                total_ventas=Sum('total')
            ).order_by('anio', 'mes')

            data = [{
                'mes': int(item['mes']),
                'anio': int(item['anio']),
                'cantidad_pedidos': item['cantidad_pedidos'],
                'total_ventas': float(item['total_ventas'] or 0)
            } for item in ventas_por_mes]

        elif 'cliente' in group_by:
            # Agrupar por cliente
            ventas_por_cliente = queryset.values(
                'usuario__nombre',
                'usuario__apellido',
                'usuario__email'
            ).annotate(
                cantidad_pedidos=Count('id'),
                total_gastado=Sum('total')
            ).order_by('-total_gastado')

            if config.get('limit'):
                ventas_por_cliente = ventas_por_cliente[:config['limit']]

            data = [{
                'cliente': f"{item['usuario__nombre']} {item['usuario__apellido']}",
                'email': item['usuario__email'],
                'cantidad_pedidos': item['cantidad_pedidos'],
                'total_gastado': float(item['total_gastado'] or 0)
            } for item in ventas_por_cliente]

        else:
            # Lista de pedidos sin agrupación
            if config.get('limit'):
                queryset = queryset[:config['limit']]

            data = [{
                'numero_pedido': pedido.numero_pedido,
                'fecha': pedido.created_at.strftime('%d/%m/%Y %H:%M'),
                'cliente': pedido.usuario.nombre_completo,
                'estado': pedido.estado,
                'total': float(pedido.total),
                'items': pedido.detalles.count()
            } for pedido in queryset.select_related('usuario')]

        metadata = {
            'total_records': len(data),
            'period': config.get('period', {}).get('label', 'Todo el tiempo'),
            'filters_applied': config.get('filters', {}),
            'grouped_by': config.get('group_by', [])
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_products_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de productos"""
        from apps.products.models import Prenda, StockPrenda

        queryset = Prenda.objects.filter(activa=True)

        # Aplicar filtros
        filters = config.get('filters', {})
        if 'categoria' in filters:
            queryset = queryset.filter(categorias__nombre__iexact=filters['categoria'])
        if 'marca' in filters:
            queryset = queryset.filter(marca__nombre__iexact=filters['marca'])

        # Agrupación
        group_by = config.get('group_by', [])

        if 'categoria' in group_by:
            # Agrupar por categoría
            from apps.products.models import Categoria

            categorias = Categoria.objects.filter(activa=True).annotate(
                cantidad_productos=Count('prendas', filter=Q(prendas__activa=True))
            ).order_by('-cantidad_productos')

            data = [{
                'categoria': cat.nombre,
                'cantidad_productos': cat.cantidad_productos
            } for cat in categorias]

        else:
            # Lista de productos
            queryset = queryset.annotate(
                stock_total=Sum('stocks__cantidad')
            ).select_related('marca')

            if config.get('limit'):
                queryset = queryset[:config['limit']]

            data = [{
                'nombre': prenda.nombre,
                'marca': prenda.marca.nombre,
                'precio': float(prenda.precio),
                'stock_total': prenda.stock_total or 0,
                'categorias': ', '.join([cat.nombre for cat in prenda.categorias.all()]),
                'activa': prenda.activa
            } for prenda in queryset.prefetch_related('categorias')]

        metadata = {
            'total_records': len(data),
            'filters_applied': config.get('filters', {}),
            'grouped_by': config.get('group_by', [])
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_customers_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de clientes"""
        from apps.accounts.models import User

        queryset = User.objects.filter(rol__nombre='Cliente')

        # Filtro de período (por fecha de registro)
        if config.get('period'):
            start_date = config['period']['start_date']
            end_date = config['period']['end_date']
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

        # Anotar con cantidad de pedidos
        queryset = queryset.annotate(
            cantidad_pedidos=Count('pedidos'),
            total_gastado=Sum('pedidos__total')
        ).order_by('-total_gastado')

        if config.get('limit'):
            queryset = queryset[:config['limit']]

        data = [{
            'nombre_completo': user.nombre_completo,
            'email': user.email,
            'telefono': user.telefono or '-',
            'fecha_registro': user.created_at.strftime('%d/%m/%Y'),
            'cantidad_pedidos': user.cantidad_pedidos,
            'total_gastado': float(user.total_gastado or 0)
        } for user in queryset]

        metadata = {
            'total_records': len(data),
            'period': config.get('period', {}).get('label', 'Todo el tiempo')
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_analytics_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de analytics/estadísticas"""
        from apps.reports.services.analytics_service import AnalyticsService

        data = {
            'resumen_general': AnalyticsService.get_summary(),
            'resumen_inventario': AnalyticsService.get_inventory_summary(),
            'resumen_clientes': AnalyticsService.get_customer_analytics(),
            'ventas_por_mes': AnalyticsService.get_sales_by_month(months=6),
            'productos_mas_vendidos': AnalyticsService.get_top_selling_products(limit=10),
            'pedidos_por_estado': AnalyticsService.get_sales_by_status(),
        }

        metadata = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'analytics'
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_logins_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de logins"""
        from apps.accounts.models import LoginAudit

        queryset = LoginAudit.objects.all()

        # Aplicar filtros de período
        if config.get('period'):
            start_date = config['period']['start_date']
            end_date = config['period']['end_date']
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

        # Ordenar por más recientes
        queryset = queryset.select_related('user').order_by('-created_at')

        # Aplicar límite si existe
        if config.get('limit'):
            queryset = queryset[:config['limit']]

        data = [{
            'usuario': login.user.nombre_completo,
            'email': login.user.email,
            'fecha_hora': login.created_at.strftime('%d/%m/%Y %H:%M:%S'),
            'ip': login.ip_address,
            'exitoso': 'Sí' if login.success else 'No'
        } for login in queryset]

        metadata = {
            'total_records': len(data),
            'period': config.get('period', {}).get('label', 'Todo el tiempo'),
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_carts_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de carritos activos"""
        from apps.cart.models import Carrito
        from django.db.models import Count

        # Carritos con items (no eliminados)
        queryset = Carrito.objects.annotate(
            num_items=Count('items', filter=Q(items__deleted_at__isnull=True))
        ).filter(num_items__gt=0).select_related('usuario')

        # Aplicar límite
        if config.get('limit'):
            queryset = queryset[:config['limit']]

        data = [{
            'usuario': carrito.usuario.nombre_completo,
            'email': carrito.usuario.email,
            'cantidad_items': carrito.total_items,
            'cantidad_productos': carrito.cantidad_total_items,
            'subtotal': float(carrito.subtotal),
            'fecha_creacion': carrito.created_at.strftime('%d/%m/%Y %H:%M')
        } for carrito in queryset]

        metadata = {
            'total_records': len(data),
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_top_products_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de productos más vendidos"""
        from apps.orders.models import DetallePedido, Pedido

        # Query base
        detalles_qs = DetallePedido.objects.select_related('prenda')

        # Filtrar por período si existe
        if config.get('period'):
            start_date = config['period']['start_date']
            end_date = config['period']['end_date']
            detalles_qs = detalles_qs.filter(
                pedido__created_at__date__gte=start_date,
                pedido__created_at__date__lte=end_date
            )

        # Agrupar por producto y ordenar
        productos_vendidos = detalles_qs.values(
            'prenda__nombre',
            'prenda__precio'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            total_ingresos=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-cantidad_vendida')

        # Aplicar límite (por defecto top 10)
        limit = config.get('limit', 10)
        productos_vendidos = productos_vendidos[:limit]

        data = [{
            'producto': item['prenda__nombre'],
            'precio_unitario': float(item['prenda__precio']),
            'cantidad_vendida': item['cantidad_vendida'],
            'total_ingresos': float(item['total_ingresos'])
        } for item in productos_vendidos]

        metadata = {
            'total_records': len(data),
            'period': config.get('period', {}).get('label', 'Todo el tiempo'),
            'limit': limit
        }

        return {
            'data': data,
            'metadata': metadata
        }

    @classmethod
    def _build_revenue_report(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Construir reporte de ingresos por período"""
        from apps.orders.models import Pedido

        queryset = Pedido.objects.all()

        # Aplicar filtros de período
        if config.get('period'):
            start_date = config['period']['start_date']
            end_date = config['period']['end_date']
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )

        # Agrupar por día
        ingresos_por_dia = queryset.extra({
            'fecha': "DATE(created_at)"
        }).values('fecha').annotate(
            cantidad_pedidos=Count('id'),
            total_ingresos=Sum('total')
        ).order_by('fecha')

        data = [{
            'fecha': item['fecha'].strftime('%d/%m/%Y') if hasattr(item['fecha'], 'strftime') else str(item['fecha']),
            'cantidad_pedidos': item['cantidad_pedidos'],
            'total_ingresos': float(item['total_ingresos'] or 0)
        } for item in ingresos_por_dia]

        # Calcular totales
        total_pedidos = sum(item['cantidad_pedidos'] for item in data)
        total_ingresos = sum(item['total_ingresos'] for item in data)

        metadata = {
            'total_records': len(data),
            'period': config.get('period', {}).get('label', 'Todo el tiempo'),
            'total_pedidos': total_pedidos,
            'total_ingresos': total_ingresos
        }

        return {
            'data': data,
            'metadata': metadata
        }
