#!/usr/bin/env python3
"""
🔧 Script Maestro - Actualizar Todos los Datos

Ejecuta todos los scripts de actualización en el orden correcto:
1. Actualizar fechas de clientes
2. Actualizar fechas de prendas
3. Limpiar nombres de prendas (quitar colores)
4. Actualizar fechas de pedidos
5. Mejorar notas de pedidos
6. Llenar carritos de clientes 1-20

Uso:
    python scripts/master_update.py
"""

import os
import sys
from pathlib import Path
import subprocess

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

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


def ejecutar_script(script_name, descripcion):
    """Ejecuta un script de Python"""
    print_header(f"EJECUTANDO: {descripcion}")
    
    script_path = BASE_DIR / 'scripts' / script_name
    
    # Usar el Python del virtualenv si existe
    if (BASE_DIR / 'vane' / 'Scripts' / 'python.exe').exists():
        python_executable = str(BASE_DIR / 'vane' / 'Scripts' / 'python.exe')
    else:
        python_executable = sys.executable
    
    try:
        result = subprocess.run(
            [python_executable, str(script_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print(f"{Colors.OK}[OK] {descripcion} completado{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}[ERROR] Error en {descripcion}{Colors.END}")
        print(e.stdout)
        print(e.stderr)
        return False


def main():
    """Ejecutar todos los scripts de actualización"""
    print_header("ACTUALIZACION MAESTRA DE DATOS")
    print(f"  {Colors.CYAN}Este proceso actualizara TODOS los datos existentes{Colors.END}")
    print(f"  {Colors.WARN}ADVERTENCIA: Este proceso modificara datos en la base de datos{Colors.END}\n")
    
    respuesta = input(f"{Colors.BOLD}Desea continuar? (s/N): {Colors.END}")
    
    if respuesta.lower() != 's':
        print(f"\n{Colors.WARN}[INFO] Operacion cancelada{Colors.END}\n")
        return
    
    scripts = [
        ('update_clientes_fechas.py', '1. Actualizar fechas de clientes'),
        ('update_prendas_fechas.py', '2. Actualizar fechas de prendas'),
        ('fix_prendas_nombres.py', '3. Limpiar nombres de prendas'),
        ('update_pedidos_fechas.py', '4. Actualizar fechas de pedidos'),
        ('fix_pedidos_notas.py', '5. Mejorar notas de pedidos'),
        ('populate_carritos.py', '6. Llenar carritos de clientes 1-20'),
    ]
    
    exitosos = 0
    fallidos = 0
    
    for script, descripcion in scripts:
        if ejecutar_script(script, descripcion):
            exitosos += 1
        else:
            fallidos += 1
            print(f"\n{Colors.WARN}[INFO] Desea continuar con los siguientes scripts? (s/N): {Colors.END}")
            respuesta = input()
            if respuesta.lower() != 's':
                break
    
    # Resumen final
    print_header("RESUMEN DE ACTUALIZACION")
    print(f"  {Colors.OK}[OK] Scripts exitosos: {exitosos}{Colors.END}")
    print(f"  {Colors.FAIL}[ERROR] Scripts fallidos: {fallidos}{Colors.END}")
    
    if fallidos == 0:
        print(f"\n{Colors.OK}[OK] Todos los datos han sido actualizados exitosamente{Colors.END}\n")
    else:
        print(f"\n{Colors.WARN}[INFO] Algunos scripts fallaron. Revise los mensajes de error.{Colors.END}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARN}[INFO] Operacion cancelada por el usuario{Colors.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}[ERROR]{Colors.END} {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
