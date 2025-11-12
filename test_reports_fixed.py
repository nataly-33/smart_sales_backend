"""
Test para verificar que todos los reportes funcionan correctamente.
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.reports.services.prompt_parser import PromptParser
from datetime import datetime

def test_prompt(prompt, expected_type=None, expected_period_label=None):
    """Probar un prompt y mostrar el resultado"""
    print(f"\n{'='*80}")
    print(f"PROMPT: {prompt}")
    print(f"{'='*80}")
    
    try:
        config = PromptParser.parse(prompt)
        print(f"✅ PARSEADO EXITOSAMENTE")
        print(f"  Tipo: {config['type']}")
        print(f"  Formato: {config['format']}")
        
        if config['period']:
            print(f"  Período: {config['period']['label']}")
            print(f"    Desde: {config['period']['start_date']}")
            print(f"    Hasta: {config['period']['end_date']}")
        else:
            print(f"  Período: Sin período específico")
        
        if config['filters']:
            print(f"  Filtros: {config['filters']}")
        
        if config['limit']:
            print(f"  Límite: {config['limit']}")
        
        # Verificar expectativas
        if expected_type and config['type'] != expected_type:
            print(f"⚠️  ADVERTENCIA: Se esperaba tipo '{expected_type}', obtuvo '{config['type']}'")
        
        if expected_period_label and config['period']:
            if expected_period_label not in config['period']['label']:
                print(f"⚠️  ADVERTENCIA: Se esperaba período con '{expected_period_label}'")
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests"""
    print(f"\n{'#'*80}")
    print(f"# TEST DE REPORTES - VERIFICACIÓN DE CORRECCIONES")
    print(f"# Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"{'#'*80}")
    
    tests = [
        # Tests de NoneType corregido
        ("Pedidos pendientes en PDF", "ventas", None),
        ("Top 50 clientes en Excel", "clientes", None),
        ("Inventario completo en Excel", "productos", None),
        
        # Tests de reconocimiento de meses
        ("Ventas de octubre 2025 en PDF", "ventas", "Octubre 2025"),
        ("Pedidos de agosto 2024 en Excel", "ventas", "Agosto 2024"),
        ("Productos vendidos en noviembre 2024", "productos", "Noviembre 2024"),
        ("Reporte de diciembre 2024 en CSV", "ventas", "Diciembre 2024"),
        
        # Tests de reconocimiento de años
        ("Ventas del año 2024 en PDF", "ventas", "2024"),
        ("Pedidos del año 2025 en Excel", "ventas", "2025"),
        ("Comparativa año 2024 vs 2025", "ventas", None),
        
        # Tests de reconocimiento de trimestres
        ("Pedidos del primer trimestre 2024 en PDF", "ventas", "Primer Trimestre 2024"),
        ("Ventas del segundo trimestre 2025", "ventas", "Segundo Trimestre 2025"),
        ("Reporte Q1 2024 en Excel", "ventas", "Primer Trimestre 2024"),
        ("Análisis Q3 2025 en PDF", "analytics", "Tercer Trimestre 2025"),
        ("Pedidos del cuarto trimestre 2024", "ventas", "Cuarto Trimestre 2024"),
        
        # Tests de reconocimiento de semestres
        ("Ventas del primer semestre 2024 en PDF", "ventas", "Primer Semestre 2024"),
        ("Pedidos del segundo semestre 2025", "ventas", "Segundo Semestre 2025"),
        ("Reporte H1 2024 en Excel", "ventas", "Primer Semestre 2024"),
        ("Análisis H2 2025 en PDF", "analytics", "Segundo Semestre 2025"),
        
        # Tests de períodos relativos
        ("Ventas de ayer en PDF", "ventas", "Ayer"),
        ("Pedidos de la anterior semana en Excel", "ventas", "Semana pasada"),
        ("Reporte de la semana pasada", "ventas", "Semana pasada"),
        
        # Tests de tipo "inventario" → "productos"
        ("Inventario completo en Excel", "productos", None),
        ("Reporte de stock actual en PDF", "productos", None),
        ("Stock de productos en CSV", "productos", None),
        
        # Tests combinados
        ("Top 20 productos vendidos en octubre 2025", "top_productos", "Octubre 2025"),
        ("Clientes del primer trimestre 2024 en Excel", "clientes", "Primer Trimestre 2024"),
        ("Ingresos del segundo semestre 2025 en PDF", "ingresos", "Segundo Semestre 2025"),
    ]
    
    results = []
    for prompt, expected_type, expected_period in tests:
        success = test_prompt(prompt, expected_type, expected_period)
        results.append((prompt, success))
    
    # Resumen
    print(f"\n{'#'*80}")
    print(f"# RESUMEN DE RESULTADOS")
    print(f"{'#'*80}")
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    print(f"\n✅ Exitosos: {passed}/{len(results)}")
    print(f"❌ Fallidos: {failed}/{len(results)}")
    
    if failed > 0:
        print(f"\nPrompts fallidos:")
        for prompt, success in results:
            if not success:
                print(f"  - {prompt}")
    
    print(f"\n{'#'*80}\n")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
