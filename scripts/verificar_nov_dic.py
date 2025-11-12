#!/usr/bin/env python3
"""
Script para verificar datos de Noviembre y Diciembre por año
"""
import os
import sys
import django
from pathlib import Path

# Configuración del entorno Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db.models import Sum, Count
from apps.orders.models import Pedido, DetallePedido
from datetime import datetime

print("="*80)
print("🔍 VERIFICACIÓN DE DATOS: NOVIEMBRE Y DICIEMBRE POR AÑO")
print("="*80)
print()

# Verificar Noviembre de cada año
print("📅 NOVIEMBRE (Mes 11):")
print("-" * 80)
for year in [2023, 2024, 2025]:
    pedidos = Pedido.objects.filter(
        created_at__year=year,
        created_at__month=11,
        estado__in=['completado', 'entregado', 'enviado']
    )
    
    total_pedidos = pedidos.count()
    
    # Sumar unidades vendidas
    detalles = DetallePedido.objects.filter(pedido__in=pedidos)
    total_unidades = detalles.aggregate(total=Sum('cantidad'))['total'] or 0
    total_ingresos = detalles.aggregate(total=Sum('subtotal'))['total'] or 0
    
    print(f"Noviembre {year}:")
    print(f"  - Pedidos: {total_pedidos}")
    print(f"  - Unidades vendidas: {total_unidades}")
    print(f"  - Ingresos: Bs {total_ingresos:,.0f}")
    print()

print()
print("📅 DICIEMBRE (Mes 12):")
print("-" * 80)
for year in [2023, 2024, 2025]:
    pedidos = Pedido.objects.filter(
        created_at__year=year,
        created_at__month=12,
        estado__in=['completado', 'entregado', 'enviado']
    )
    
    total_pedidos = pedidos.count()
    
    # Sumar unidades vendidas
    detalles = DetallePedido.objects.filter(pedido__in=pedidos)
    total_unidades = detalles.aggregate(total=Sum('cantidad'))['total'] or 0
    total_ingresos = detalles.aggregate(total=Sum('subtotal'))['total'] or 0
    
    print(f"Diciembre {year}:")
    print(f"  - Pedidos: {total_pedidos}")
    print(f"  - Unidades vendidas: {total_unidades}")
    print(f"  - Ingresos: Bs {total_ingresos:,.0f}")
    print()

print()
print("="*80)
print("📊 ANÁLISIS:")
print("="*80)

# Comparar Noviembre
nov_2023 = DetallePedido.objects.filter(
    pedido__created_at__year=2023,
    pedido__created_at__month=11,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

nov_2024 = DetallePedido.objects.filter(
    pedido__created_at__year=2024,
    pedido__created_at__month=11,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

nov_2025 = DetallePedido.objects.filter(
    pedido__created_at__year=2025,
    pedido__created_at__month=11,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

print(f"\n📈 CRECIMIENTO NOVIEMBRE:")
if nov_2023 > 0:
    crecimiento_2024 = ((nov_2024 - nov_2023) / nov_2023) * 100
    print(f"  2023 → 2024: {crecimiento_2024:+.1f}%  ({nov_2023} → {nov_2024})")
if nov_2024 > 0:
    crecimiento_2025 = ((nov_2025 - nov_2024) / nov_2024) * 100
    print(f"  2024 → 2025: {crecimiento_2025:+.1f}%  ({nov_2024} → {nov_2025})")

# Comparar Diciembre
dic_2023 = DetallePedido.objects.filter(
    pedido__created_at__year=2023,
    pedido__created_at__month=12,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

dic_2024 = DetallePedido.objects.filter(
    pedido__created_at__year=2024,
    pedido__created_at__month=12,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

dic_2025 = DetallePedido.objects.filter(
    pedido__created_at__year=2025,
    pedido__created_at__month=12,
    pedido__estado__in=['completado', 'entregado', 'enviado']
).aggregate(total=Sum('cantidad'))['total'] or 0

print(f"\n📈 CRECIMIENTO DICIEMBRE:")
if dic_2023 > 0:
    crecimiento_2024 = ((dic_2024 - dic_2023) / dic_2023) * 100
    print(f"  2023 → 2024: {crecimiento_2024:+.1f}%  ({dic_2023} → {dic_2024})")
if dic_2024 > 0:
    crecimiento_2025 = ((dic_2025 - dic_2024) / dic_2024) * 100
    print(f"  2024 → 2025: {crecimiento_2025:+.1f}%  ({dic_2024} → {dic_2025})")
    print(f"\n  ⚠️  Nota: Dic 2025 = {dic_2025} (mes actual, puede estar incompleto)")

print()
print("="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80)
