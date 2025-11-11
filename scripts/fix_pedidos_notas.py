#!/usr/bin/env python3
"""
📝 Mejorar Notas de Pedidos

Reemplaza notas genéricas o sin sentido por notas realistas usando Faker.

Usa:
    python scripts/fix_pedidos_notas.py
"""

import os
import sys
import random
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

import django
django.setup()

from django.db import transaction
from faker import Faker
from apps.orders.models import Pedido

fake = Faker('es_ES')

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


NOTAS_PLANTILLAS = [
    "Por favor, entregar antes de las 18:00",
    "Dejar con el portero si no estoy",
    "Tocar el timbre dos veces",
    "Llamar antes de entregar",
    "Es un regalo, por favor envolver con cuidado",
    "Entregar en la oficina, segundo piso",
    "Prefiero entrega en horario de mañana",
    "Si no hay nadie, dejar en recepción",
    "Envío urgente, favor priorizar",
    "Verificar tallas antes de enviar",
    "Incluir factura en el paquete",
    "Empacar por separado cada prenda",
    "Notificar cuando esté en camino",
    "Entregar solo en manos del destinatario",
    "Es para un evento el fin de semana",
    "",  # Sin notas (30% de los casos)
    "",
    "",
]


def generar_nota_realista():
    """Genera una nota de cliente realista"""
    # 30% sin nota
    if random.random() < 0.3:
        return ""
    
    # 70% con nota de plantilla o generada
    if random.random() < 0.7:
        return random.choice(NOTAS_PLANTILLAS)
    else:
        # Generar nota personalizada
        opciones = [
            f"Entregar en {fake.street_address()}",
            f"Contactar al {fake.phone_number()} antes de llegar",
            f"Buzón negro en la entrada, dejar ahí si no respondo",
            f"Entrega para {fake.name()}, departamento {random.randint(101, 605)}",
            f"Cuidado con el perro, tocar suave",
            f"Horario preferido: {random.randint(9, 18)}:00-{random.randint(9, 18)}:00",
        ]
        return random.choice(opciones)


@transaction.atomic
def fix_notas_pedidos():
    """Actualizar notas de todos los pedidos"""
    print_header("MEJORANDO NOTAS DE PEDIDOS")
    
    pedidos = Pedido.objects.all().order_by('id')
    total = pedidos.count()
    
    print(f"{Colors.CYAN}Total de pedidos: {total}{Colors.END}\n")
    
    actualizados = 0
    
    for idx, pedido in enumerate(pedidos, start=1):
        nueva_nota = generar_nota_realista()
        
        pedido.notas_cliente = nueva_nota
        pedido.save(update_fields=['notas_cliente'])
        
        actualizados += 1
        
        if idx % 100 == 0:
            porcentaje = (idx / total) * 100
            print(f"  {Colors.CYAN}[{idx:4}/{total}] {porcentaje:5.1f}%{Colors.END} Actualizando...")
    
    print(f"\n{Colors.OK}[OK] {actualizados} pedidos actualizados{Colors.END}")
    
    # Estadisticas
    con_notas = Pedido.objects.exclude(notas_cliente='').count()
    sin_notas = Pedido.objects.filter(notas_cliente='').count()
    
    print(f"\n{Colors.BOLD}ESTADISTICAS:{Colors.END}")
    print(f"  - Pedidos con notas: {con_notas} ({con_notas/total*100:.1f}%)")
    print(f"  - Pedidos sin notas: {sin_notas} ({sin_notas/total*100:.1f}%)")


if __name__ == '__main__':
    try:
        fix_notas_pedidos()
        print(f"\n{Colors.OK}[OK] Actualizacion completada{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
