"""
Script para probar TODOS los reportes del sistema
Ejecuta cada prompt de la lista y verifica que funcione
"""

import os
import sys
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.reports.services.report_generator_service import ReportGeneratorService, ReportGeneratorServiceError

# Lista de TODOS los prompts a probar
PROMPTS_TO_TEST = [
    # Ventas
    ("Ventas del año 2025 en Excel", "excel"),
    ("Ventas del último mes en PDF", "pdf"),
    ("Ventas agrupadas por producto del año 2025 en Excel", "excel"),
    ("Pedidos pendientes en PDF", "pdf"),
    
    # Productos
    ("Top 10 productos más vendidos en PDF", "pdf"),
    ("Top 5 productos más vendidos del año 2025 en Excel", "excel"),
    ("Inventario completo en Excel", "excel"),
    ("Productos agrupados por categoría en PDF", "pdf"),
    
    # Clientes
    ("Clientes del año 2025 en Excel", "excel"),
    ("Clientes del último mes en CSV", "csv"),
    ("Top 10 clientes con más compras en PDF", "pdf"),
    
    # Analytics
    ("Reporte de analytics completo en PDF", "pdf"),
    ("Logins de los últimos 7 días en Excel", "excel"),
    ("Logins de hoy en CSV", "csv"),
    ("Logins de los últimos 30 días en Excel", "excel"),
    
    # Carritos e Ingresos
    ("Carritos activos con items en PDF", "pdf"),
    ("Ingresos por día del mes actual en Excel", "excel"),
    ("Ingresos del año 2025 en Excel", "excel"),
    
    # Reportes 2024
    ("Ventas del año 2024 en PDF", "pdf"),
    ("Top 10 productos más vendidos de 2024 en Excel", "excel"),
    ("Clientes registrados en 2024 en CSV", "csv"),
]

def test_report(prompt, expected_format, index, total):
    """Probar un reporte individual"""
    print(f"\n[{index}/{total}] Probando: {prompt}")
    print(f"    Formato esperado: {expected_format}")
    
    try:
        file_content, filename, mime_type = ReportGeneratorService.generate_from_prompt(
            prompt=prompt,
            user_name="Sistema Test",
            organization_name="SmartSales365",
            format_override=expected_format  # Forzar formato
        )
        
        # Verificar que se generó contenido
        if not file_content:
            print(f"    [ERROR] No se generó contenido")
            return False
        
        # Verificar tipo MIME correcto
        expected_mimes = {
            'pdf': 'application/pdf',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv'
        }
        
        if mime_type != expected_mimes.get(expected_format):
            print(f"    [ERROR] MIME incorrecto: {mime_type} (esperado: {expected_mimes.get(expected_format)})")
            return False
        
        print(f"    [OK] Generado correctamente: {filename} ({len(file_content)} bytes)")
        return True
        
    except ReportGeneratorServiceError as e:
        print(f"    [ERROR] Error del servicio: {e}")
        return False
    except Exception as e:
        print(f"    [ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("=" * 80)
    print("PRUEBA AUTOMATICA DE TODOS LOS REPORTES")
    print("=" * 80)
    print(f"Total de reportes a probar: {len(PROMPTS_TO_TEST)}")
    print("=" * 80)
    
    exitosos = 0
    fallidos = 0
    errores = []
    
    for index, (prompt, expected_format) in enumerate(PROMPTS_TO_TEST, start=1):
        if test_report(prompt, expected_format, index, len(PROMPTS_TO_TEST)):
            exitosos += 1
        else:
            fallidos += 1
            errores.append(prompt)
    
    print("\n" + "=" * 80)
    print("RESUMEN FINAL")
    print("=" * 80)
    print(f"[OK] Exitosos: {exitosos}/{len(PROMPTS_TO_TEST)}")
    print(f"[ERROR] Fallidos: {fallidos}/{len(PROMPTS_TO_TEST)}")
    
    if errores:
        print("\nReportes que fallaron:")
        for error in errores:
            print(f"  - {error}")
    else:
        print("\n[OK] TODOS LOS REPORTES FUNCIONAN CORRECTAMENTE!")
    
    print("=" * 80)
    
    # Retornar código de salida
    return 0 if fallidos == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
