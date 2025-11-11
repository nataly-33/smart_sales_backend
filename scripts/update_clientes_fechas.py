#!/usr/bin/env python3
"""
👥 Actualizar Fechas de Clientes

Modifica las fechas de registro (created_at) de todos los clientes para
distribuirlas desde enero 2024 hasta hoy (11 noviembre 2025).

Uso:
    python scripts/update_clientes_fechas.py
"""

import os
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

from django.db import transaction
from apps.accounts.models import User

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
    
    dias_diferencia = (fecha_fin - fecha_inicio).days
    dias_random = random.randint(0, dias_diferencia)
    fecha_aleatoria = fecha_inicio + timedelta(days=dias_random)
    
    hora_random = random.randint(0, 23)
    minuto_random = random.randint(0, 59)
    segundo_random = random.randint(0, 59)
    
    return fecha_aleatoria.replace(hour=hora_random, minute=minuto_random, second=segundo_random)


@transaction.atomic
def actualizar_fechas_clientes():
    """Actualizar fechas de todos los clientes (rol Cliente)"""
    print_header("ACTUALIZANDO FECHAS DE CLIENTES")
    
    # Solo actualizar usuarios con rol Cliente
    clientes = User.objects.filter(rol__nombre='Cliente').order_by('id')
    total = clientes.count()
    
    print(f"{Colors.CYAN}Total de clientes: {total}{Colors.END}\n")
    
    actualizados = 0
    
    for idx, cliente in enumerate(clientes, start=1):
        nueva_fecha = generar_fecha_aleatoria()
        
        cliente.created_at = nueva_fecha
        cliente.updated_at = nueva_fecha + timedelta(hours=random.randint(0, 24))
        cliente.save(update_fields=['created_at', 'updated_at'])
        
        actualizados += 1
        
        if idx % 50 == 0:
            porcentaje = (idx / total) * 100
            print(f"  {Colors.CYAN}[{idx:4}/{total}] {porcentaje:5.1f}%{Colors.END} Actualizando...")
    
    print(f"\n{Colors.OK}[OK] {actualizados} clientes actualizados{Colors.END}")
    
    # Estadisticas por año
    clientes_2024 = User.objects.filter(rol__nombre='Cliente', created_at__year=2024).count()
    clientes_2025 = User.objects.filter(rol__nombre='Cliente', created_at__year=2025).count()
    
    print(f"\n{Colors.BOLD}ESTADISTICAS:{Colors.END}")
    print(f"  - Clientes registrados en 2024: {clientes_2024}")
    print(f"  - Clientes registrados en 2025: {clientes_2025}")


if __name__ == '__main__':
    try:
        actualizar_fechas_clientes()
        print(f"\n{Colors.OK}[OK] Actualizacion completada{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
