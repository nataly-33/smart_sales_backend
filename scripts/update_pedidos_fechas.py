#!/usr/bin/env python3
"""
📅 Actualizar Fechas de Pedidos

Modifica las fechas de creación de todos los pedidos para distribuirlas
desde enero 2024 hasta hoy (11 noviembre 2025).

Uso:
    python scripts/update_pedidos_fechas.py
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

from django.db import transaction
from apps.orders.models import Pedido

# Colores ANSI
class Colors:
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(texto):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{texto}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")


def generar_fecha_aleatoria():
    """Genera una fecha aleatoria entre enero 2024 y hoy"""
    fecha_inicio = datetime(2024, 1, 1)
    fecha_fin = datetime(2025, 11, 11, 23, 59, 59)
    
    # Calcular días entre fechas
    dias_diferencia = (fecha_fin - fecha_inicio).days
    
    # Generar fecha aleatoria
    dias_random = random.randint(0, dias_diferencia)
    fecha_aleatoria = fecha_inicio + timedelta(days=dias_random)
    
    # Agregar horas y minutos aleatorios
    hora_random = random.randint(0, 23)
    minuto_random = random.randint(0, 59)
    segundo_random = random.randint(0, 59)
    
    return fecha_aleatoria.replace(hour=hora_random, minute=minuto_random, second=segundo_random)


@transaction.atomic
def actualizar_fechas_pedidos():
    """Actualizar fechas de todos los pedidos"""
    print_header("ACTUALIZANDO FECHAS DE PEDIDOS")
    
    pedidos = Pedido.objects.all().order_by('id')
    total = pedidos.count()
    
    print(f"{Colors.CYAN}Total de pedidos: {total}{Colors.END}\n")
    
    actualizados = 0
    
    for idx, pedido in enumerate(pedidos, start=1):
        # Generar fecha aleatoria
        nueva_fecha = generar_fecha_aleatoria()
        
        # Actualizar created_at y updated_at
        pedido.created_at = nueva_fecha
        pedido.updated_at = nueva_fecha + timedelta(hours=random.randint(1, 48))
        pedido.save(update_fields=['created_at', 'updated_at'])
        
        actualizados += 1
        
        if idx % 50 == 0:
            porcentaje = (idx / total) * 100
            print(f"  {Colors.CYAN}[{idx:4}/{total}] {porcentaje:5.1f}%{Colors.END} Actualizando...")
    
    print(f"\n{Colors.OK}[OK] {actualizados} pedidos actualizados{Colors.END}")
    
    # Mostrar estadisticas por año
    pedidos_2024 = Pedido.objects.filter(created_at__year=2024).count()
    pedidos_2025 = Pedido.objects.filter(created_at__year=2025).count()
    
    print(f"\n{Colors.BOLD}ESTADISTICAS:{Colors.END}")
    print(f"  - Pedidos 2024: {pedidos_2024}")
    print(f"  - Pedidos 2025: {pedidos_2025}")


if __name__ == '__main__':
    try:
        actualizar_fechas_pedidos()
        print(f"\n{Colors.OK}[OK] Actualizacion completada{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
