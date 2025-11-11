#!/usr/bin/env python3
"""
🔍 AUDITORÍA COMPLETA DE DATOS DE VENTAS
Verifica la consistencia de los datos en la base de datos
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db.models import Sum, Count, Avg
from apps.orders.models import Pedido, DetallePedido
from apps.products.models import Prenda

print("=" * 80)
print("🔍 AUDITORÍA DE DATOS DE VENTAS")
print("=" * 80)

# 1. Pedidos por año y mes
print("\n📊 PEDIDOS POR AÑO Y MES:")
print("-" * 80)

pedidos_completados = Pedido.objects.filter(
    estado__in=['completado', 'enviado', 'entregado']
)

for year in [2023, 2024, 2025]:
    print(f"\n🗓️  AÑO {year}:")
    for month in range(1, 13):
        pedidos = pedidos_completados.filter(
            created_at__year=year,
            created_at__month=month
        )
        count = pedidos.count()
        
        # Cantidad total vendida
        detalles = DetallePedido.objects.filter(
            pedido__in=pedidos
        ).aggregate(
            total_cantidad=Sum('cantidad'),
            total_ingresos=Sum('subtotal')
        )
        
        cantidad = detalles['total_cantidad'] or 0
        ingresos = detalles['total_ingresos'] or 0
        
        if count > 0:
            print(f"  Mes {month:2d}: {count:4d} pedidos | {cantidad:5d} unidades | Bs {ingresos:,.0f}")

# 2. Ventas por categoría en 2025
print("\n" + "=" * 80)
print("📦 VENTAS POR CATEGORÍA EN 2025:")
print("-" * 80)

categorias = ['Blusas', 'Vestidos', 'Jeans', 'Jackets']

for mes in range(1, 13):
    print(f"\nMes {mes:2d} (2025):")
    
    for categoria in categorias:
        # Obtener prendas de esta categoría
        prendas_cat = Prenda.objects.filter(categorias__nombre=categoria)
        
        # Detalles vendidos de estas prendas en este mes
        detalles = DetallePedido.objects.filter(
            prenda__in=prendas_cat,
            pedido__created_at__year=2025,
            pedido__created_at__month=mes,
            pedido__estado__in=['completado', 'enviado', 'entregado']
        ).aggregate(
            total=Sum('cantidad')
        )
        
        cantidad = detalles['total'] or 0
        print(f"  {categoria:10s}: {cantidad:4d} unidades")

# 3. Totales generales
print("\n" + "=" * 80)
print("📈 TOTALES GENERALES:")
print("-" * 80)

for year in [2023, 2024, 2025]:
    pedidos = pedidos_completados.filter(created_at__year=year)
    detalles = DetallePedido.objects.filter(
        pedido__in=pedidos
    ).aggregate(
        total_pedidos=Count('pedido', distinct=True),
        total_cantidad=Sum('cantidad'),
        total_ingresos=Sum('subtotal')
    )
    
    print(f"\n{year}:")
    print(f"  Pedidos: {detalles['total_pedidos']}")
    print(f"  Unidades vendidas: {detalles['total_cantidad']}")
    print(f"  Ingresos: Bs {detalles['total_ingresos']:,.0f}")

# 4. Verificar noviembre específicamente
print("\n" + "=" * 80)
print("🔍 COMPARACIÓN NOVIEMBRE 2025:")
print("-" * 80)

nov_pedidos = pedidos_completados.filter(
    created_at__year=2025,
    created_at__month=11
)

nov_detalles = DetallePedido.objects.filter(
    pedido__in=nov_pedidos
).aggregate(
    total_cantidad=Sum('cantidad'),
    total_ingresos=Sum('subtotal')
)

print(f"Pedidos en noviembre: {nov_pedidos.count()}")
print(f"Unidades vendidas: {nov_detalles['total_cantidad']}")
print(f"Ingresos: Bs {nov_detalles['total_ingresos']:,.0f}")

print("\n" + "=" * 80)
print("✅ AUDITORÍA COMPLETADA")
print("=" * 80)
