#!/usr/bin/env python3
"""
🛒 Llenar Carritos de Clientes 1-20

Crea carritos con productos para los clientes cliente_1@example.com hasta
cliente_20@example.com.

Uso:
    python scripts/populate_carritos.py
"""

import os
import sys
import random
from pathlib import Path
from decimal import Decimal

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

from django.db import transaction
from apps.accounts.models import User
from apps.products.models import Prenda, Talla
from apps.cart.models import Carrito, ItemCarrito

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


@transaction.atomic
def populate_carritos():
    """Llenar carritos de clientes 1-20"""
    print_header("LLENANDO CARRITOS DE CLIENTES 1-20")
    
    # Obtener clientes
    clientes = []
    for i in range(1, 21):
        email = f"cliente_{i}@example.com"
        try:
            cliente = User.objects.get(email=email)
            clientes.append(cliente)
        except User.DoesNotExist:
            print(f"{Colors.WARN}[INFO] Cliente {email} no existe{Colors.END}")
    
    if not clientes:
        print(f"{Colors.FAIL}[ERROR] No se encontraron clientes{Colors.END}")
        return
    
    print(f"{Colors.CYAN}Clientes encontrados: {len(clientes)}{Colors.END}\n")
    
    # Obtener prendas activas
    prendas = list(Prenda.objects.filter(activa=True))
    tallas = list(Talla.objects.all())
    
    if not prendas:
        print(f"{Colors.FAIL}[ERROR] No hay prendas disponibles{Colors.END}")
        return
    
    carritos_creados = 0
    items_creados = 0
    
    for idx, cliente in enumerate(clientes, start=1):
        # Obtener o crear carrito
        carrito, created = Carrito.objects.get_or_create(
            usuario=cliente
        )
        
        if created:
            carritos_creados += 1
        else:
            # Limpiar items existentes
            ItemCarrito.objects.filter(carrito=carrito).delete()
        
        # Agregar 2-8 items al carrito
        num_items = random.randint(2, 8)
        prendas_seleccionadas = random.sample(prendas, min(num_items, len(prendas)))
        
        for prenda in prendas_seleccionadas:
            talla = random.choice(tallas)
            cantidad = random.randint(1, 3)
            
            ItemCarrito.objects.create(
                carrito=carrito,
                prenda=prenda,
                talla=talla,
                cantidad=cantidad,
                precio_unitario=prenda.precio
            )
            items_creados += 1
        
        # Calcular total del carrito (property calculada automáticamente)
        total = carrito.total
        
        print(f"  {Colors.CYAN}[OK]{Colors.END} {cliente.email}: {num_items} items (Total: Bs. {total:.2f})")
    
    print(f"\n{Colors.OK}[OK] {carritos_creados} carritos creados/actualizados{Colors.END}")
    print(f"{Colors.OK}[OK] {items_creados} items agregados en total{Colors.END}")
    
    # Estadisticas
    promedio_items = items_creados / len(clientes)
    print(f"\n{Colors.BOLD}ESTADISTICAS:{Colors.END}")
    print(f"  - Promedio de items por carrito: {promedio_items:.1f}")


if __name__ == '__main__':
    try:
        populate_carritos()
        print(f"\n{Colors.OK}[OK] Carritos poblados exitosamente{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
