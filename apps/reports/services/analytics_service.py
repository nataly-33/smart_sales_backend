"""
Servicio de Analytics

Proporciona métricas y estadísticas del sistema de ventas.
"""

from django.db.models import Count, Sum, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Servicio para obtener métricas y análisis del sistema.
    """

    @staticmethod
    def get_sales_by_month(months=12):
        """
        Obtener ventas agrupadas por mes.

        Args:
            months: Número de meses hacia atrás

        Returns:
            list: Lista de diccionarios con {month, total_sales, order_count}
        """
        from apps.orders.models import Pedido

        today = timezone.now()
        data = []

        for i in range(months - 1, -1, -1):
            # Calcular el mes
            month_date = today - timedelta(days=30*i)
            month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            _, last_day = monthrange(month_date.year, month_date.month)
            month_end = month_date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

            # Obtener pedidos del mes (solo confirmados y completados)
            pedidos = Pedido.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end,
                estado__in=['pago_recibido', 'confirmado', 'preparando', 'enviado', 'entregado']
            )

            total_sales = pedidos.aggregate(total=Sum('total'))['total'] or 0
            order_count = pedidos.count()

            data.append({
                'month': month_date.strftime('%b %Y'),
                'total_sales': float(total_sales),
                'order_count': order_count,
                'date': month_date.isoformat()
            })

        return data

    @staticmethod
    def get_products_by_category():
        """
        Obtener cantidad de productos por categoría.

        Returns:
            list: Lista de diccionarios con {category, count}
        """
        from apps.products.models import Prenda, Categoria

        data = []
        categorias = Categoria.objects.filter(activa=True)

        for categoria in categorias:
            count = Prenda.objects.filter(
                categorias=categoria,
                activa=True
            ).count()

            data.append({
                'category': categoria.nombre,
                'count': count
            })

        return data

    @staticmethod
    def get_top_selling_products(limit=10):
        """
        Obtener productos más vendidos.

        Args:
            limit: Cantidad de productos a retornar

        Returns:
            list: Lista de productos con cantidad vendida
        """
        from apps.orders.models import DetallePedido

        products = DetallePedido.objects.values(
            'prenda__nombre',
            'prenda__precio'
        ).annotate(
            total_quantity=Sum('cantidad'),
            total_revenue=Sum(F('cantidad') * F('precio_unitario'))
        ).order_by('-total_quantity')[:limit]

        return [{
            'product_name': p['prenda__nombre'],
            'price': float(p['prenda__precio']),
            'quantity_sold': p['total_quantity'],
            'total_revenue': float(p['total_revenue'])
        } for p in products]

    @staticmethod
    def get_sales_by_status():
        """
        Obtener resumen de pedidos por estado.

        Returns:
            list: Lista con {status, count, total_amount}
        """
        from apps.orders.models import Pedido

        estados = Pedido.objects.values('estado').annotate(
            count=Count('id'),
            total_amount=Sum('total')
        ).order_by('-count')

        return [{
            'status': e['estado'],
            'count': e['count'],
            'total_amount': float(e['total_amount'] or 0)
        } for e in estados]

    @staticmethod
    def get_activity_by_day(days=30):
        """
        Obtener actividad del sistema por día (basado en creación de pedidos).

        Args:
            days: Número de días hacia atrás

        Returns:
            list: Lista de diccionarios con {day, orders, total_sales}
        """
        from apps.orders.models import Pedido

        today = timezone.now()
        data = []

        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)

            pedidos = Pedido.objects.filter(
                created_at__gte=day_start,
                created_at__lte=day_end
            )

            order_count = pedidos.count()
            total_sales = pedidos.aggregate(total=Sum('total'))['total'] or 0

            data.append({
                'day': day.strftime('%a %d'),
                'orders': order_count,
                'total_sales': float(total_sales),
                'date': day.isoformat()
            })

        return data

    @staticmethod
    def get_summary():
        """
        Obtener resumen general del sistema.

        Returns:
            dict: Diccionario con estadísticas generales
        """
        from apps.orders.models import Pedido
        from apps.products.models import Prenda
        from apps.accounts.models import User

        today = timezone.now()
        month_ago = today - timedelta(days=30)
        week_ago = today - timedelta(days=7)

        # Pedidos
        total_orders = Pedido.objects.count()
        orders_this_month = Pedido.objects.filter(created_at__gte=month_ago).count()
        orders_this_week = Pedido.objects.filter(created_at__gte=week_ago).count()

        # Ventas
        total_sales = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0
        sales_this_month = Pedido.objects.filter(
            created_at__gte=month_ago
        ).aggregate(total=Sum('total'))['total'] or 0

        # Productos
        total_products = Prenda.objects.filter(activa=True).count()
        products_low_stock = Prenda.objects.annotate(
            total_stock=Sum('stocks__cantidad')
        ).filter(total_stock__lte=10).count()

        # Clientes
        total_customers = User.objects.filter(rol__nombre='Cliente').count()
        customers_this_month = User.objects.filter(
            rol__nombre='Cliente',
            created_at__gte=month_ago
        ).count()

        return {
            'total_orders': total_orders,
            'orders_this_month': orders_this_month,
            'orders_this_week': orders_this_week,
            'total_sales': float(total_sales),
            'sales_this_month': float(sales_this_month),
            'total_products': total_products,
            'products_low_stock': products_low_stock,
            'total_customers': total_customers,
            'customers_this_month': customers_this_month,
        }

    @staticmethod
    def get_inventory_summary():
        """
        Obtener resumen de inventario.

        Returns:
            dict: Diccionario con estadísticas de inventario
        """
        from apps.products.models import Prenda, StockPrenda

        total_products = Prenda.objects.filter(activa=True).count()
        total_stock = StockPrenda.objects.aggregate(total=Sum('cantidad'))['total'] or 0

        low_stock = StockPrenda.objects.filter(
            cantidad__lte=F('stock_minimo')
        ).count()

        out_of_stock = StockPrenda.objects.filter(cantidad=0).count()

        return {
            'total_products': total_products,
            'total_stock': total_stock,
            'low_stock_items': low_stock,
            'out_of_stock_items': out_of_stock,
        }

    @staticmethod
    def get_customer_analytics():
        """
        Obtener análisis de clientes.

        Returns:
            dict: Estadísticas de clientes
        """
        from apps.accounts.models import User
        from apps.orders.models import Pedido

        total_customers = User.objects.filter(rol__nombre='Cliente').count()

        # Clientes con pedidos
        customers_with_orders = User.objects.filter(
            rol__nombre='Cliente',
            pedidos__isnull=False
        ).distinct().count()

        # Cliente con más pedidos
        top_customer = User.objects.filter(
            rol__nombre='Cliente'
        ).annotate(
            order_count=Count('pedidos')
        ).order_by('-order_count').first()

        # Valor promedio de pedido
        avg_order_value = Pedido.objects.aggregate(avg=Avg('total'))['avg'] or 0

        return {
            'total_customers': total_customers,
            'customers_with_orders': customers_with_orders,
            'customers_without_orders': total_customers - customers_with_orders,
            'top_customer': {
                'name': top_customer.nombre_completo if top_customer else None,
                'order_count': top_customer.order_count if top_customer else 0
            } if top_customer else None,
            'average_order_value': float(avg_order_value),
        }
