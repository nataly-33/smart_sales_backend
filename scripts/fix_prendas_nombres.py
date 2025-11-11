#!/usr/bin/env python3
"""
✏️ Limpiar Nombres de Prendas

Elimina los nombres de colores del campo 'nombre' de las prendas para evitar
que choquen con el color real de las imágenes.

Ejemplo:
    "Blusa Crop Top Negro" → "Blusa Crop Top"
    "Vestido Floral Rosa" → "Vestido Floral"

Uso:
    python scripts/fix_prendas_nombres.py
"""

import os
import sys
import re
from pathlib import Path

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


# Lista de colores a eliminar
COLORES = [
    'Negro', 'Blanco', 'Gris', 'Rojo', 'Azul', 'Verde', 'Amarillo',
    'Naranja', 'Rosa', 'Púrpura', 'Morado', 'Marrón', 'Beige', 'Marfil', 
    'Turquesa', 'Coral', 'Champagne', 'Marino', 'Burdeos', 'Teal', 
    'Mostaza', 'Denim', 'Celeste', 'Violeta', 'Fucsia', 'Lavanda'
]


def limpiar_nombre(nombre):
    """Elimina el color del final del nombre de la prenda"""
    nombre_limpio = nombre.strip()
    
    # Buscar si termina con algún color
    for color in COLORES:
        # Patrón: nombre + espacio + color al final
        pattern = rf'\s+{re.escape(color)}$'
        if re.search(pattern, nombre_limpio, re.IGNORECASE):
            nombre_limpio = re.sub(pattern, '', nombre_limpio, flags=re.IGNORECASE).strip()
            return nombre_limpio, True
    
    return nombre_limpio, False


@transaction.atomic
def fix_nombres_prendas():
    """Limpiar nombres de todas las prendas"""
    print_header("LIMPIANDO NOMBRES DE PRENDAS")
    
    prendas = Prenda.objects.all().order_by('id')
    total = prendas.count()
    
    print(f"{Colors.CYAN}Total de prendas: {total}{Colors.END}\n")
    
    modificados = 0
    sin_cambios = 0
    
    for idx, prenda in enumerate(prendas, start=1):
        nombre_original = prenda.nombre
        nombre_limpio, fue_modificado = limpiar_nombre(nombre_original)
        
        if fue_modificado:
            prenda.nombre = nombre_limpio
            prenda.save(update_fields=['nombre'])
            modificados += 1
            
            if modificados <= 10:  # Mostrar primeros 10 ejemplos
                print(f"  {Colors.CYAN}[OK]{Colors.END} '{nombre_original}' -> '{nombre_limpio}'")
        else:
            sin_cambios += 1
        
        if idx % 200 == 0:
            porcentaje = (idx / total) * 100
            print(f"  {Colors.BLUE}[{idx:4}/{total}] {porcentaje:5.1f}%{Colors.END} Procesando...")
    
    print(f"\n{Colors.OK}[OK] {modificados} prendas renombradas{Colors.END}")
    print(f"{Colors.WARN}[INFO] {sin_cambios} prendas sin cambios{Colors.END}")


if __name__ == '__main__':
    try:
        fix_nombres_prendas()
        print(f"\n{Colors.OK}[OK] Limpieza completada{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
