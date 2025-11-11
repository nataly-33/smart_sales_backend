#!/usr/bin/env python3
"""
🎨 Actualizar Fechas de Prendas

Modifica las fechas de creación de todas las prendas para distribuirlas
desde enero 2024 hasta hoy (11 noviembre 2025).

Uso:
    python scripts/update_prendas_fechas.py
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
from apps.products.models import Prenda

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
def actualizar_fechas_prendas():
    """Actualizar fechas de todas las prendas"""
    print_header("ACTUALIZANDO FECHAS DE PRENDAS")
    
    prendas = Prenda.objects.all().order_by('id')
    total = prendas.count()
    
    print(f"{Colors.CYAN}Total de prendas: {total}{Colors.END}\n")
    
    actualizados = 0
    
    for idx, prenda in enumerate(prendas, start=1):
        nueva_fecha = generar_fecha_aleatoria()
        
        prenda.created_at = nueva_fecha
        prenda.updated_at = nueva_fecha + timedelta(hours=random.randint(1, 24))
        prenda.save(update_fields=['created_at', 'updated_at'])
        
        actualizados += 1
        
        if idx % 100 == 0:
            porcentaje = (idx / total) * 100
            print(f"  {Colors.CYAN}[{idx:4}/{total}] {porcentaje:5.1f}%{Colors.END} Actualizando...")
    
    print(f"\n{Colors.OK}[OK] {actualizados} prendas actualizadas{Colors.END}")
    
    # Estadisticas por año
    prendas_2024 = Prenda.objects.filter(created_at__year=2024).count()
    prendas_2025 = Prenda.objects.filter(created_at__year=2025).count()
    
    print(f"\n{Colors.BOLD}ESTADISTICAS:{Colors.END}")
    print(f"  - Prendas agregadas en 2024: {prendas_2024}")
    print(f"  - Prendas agregadas en 2025: {prendas_2025}")


if __name__ == '__main__':
    try:
        actualizar_fechas_prendas()
        print(f"\n{Colors.OK}[OK] Actualizacion completada{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
