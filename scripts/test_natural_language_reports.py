"""
Script para probar los ejemplos de reportes en lenguaje natural
y verificar que generan los datos correctos.
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.reports.services.prompt_parser import PromptParser
from apps.reports.services.query_builder import QueryBuilder
from apps.orders.models import Pedido, DetallePedido
from apps.products.models import Prenda, Categoria
from apps.accounts.models import User
from django.db.models import Count, Sum, Q

# Ejemplos a probar
EXAMPLES = [
    "Ventas del año 2025 en PDF",
    "Top 10 productos más vendidos en Excel",
    "Clientes registrados este año en CSV",
    "Ventas del 01/11/2024 al 01/05/2025 en Excel",
    "Pedidos del primer trimestre 2024 en PDF",
    "Reporte de ventas agrupadas por categoría en Excel",
    "Top 5 clientes con más compras del año 2025 en PDF",
    "Ventas agrupadas por mes del año 2024 en CSV",
    "Productos más vendidos agrupados por categoría en Excel",
    "Pedidos del último semestre agrupados por cliente en PDF"
]

def print_separator(char="="):
    print(char * 80)

def test_prompt_parsing(prompt):
    """Prueba el parsing del prompt"""
    print(f"\n🔍 PROMPT: {prompt}")
    print_separator("-")
    
    parser = PromptParser()
    parsed = parser.parse(prompt)
    
    print("📋 Parsed Data:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")
    
    return parsed

def test_query_execution(parsed_data):
    """Ejecuta la query y muestra resultados"""
    print("\n🔧 Building Query...")
    
    result = QueryBuilder.build(parsed_data)
    
    data = result.get('data', [])
    metadata = result.get('metadata', {})
    
    print(f"📊 Query Type: {parsed_data.get('type')}")
    print(f"� Total Results: {len(data)}")
    print(f"� Metadata: {metadata}")
    
    # Mostrar los primeros 5 resultados
    if len(data) > 0:
        print("\n📄 Sample Results (first 5):")
        for i, item in enumerate(data[:5], 1):
            print(f"\n  {i}. {item}")
    
    return result

def verify_date_range(result, start_date, end_date):
    """Verifica que los resultados estén en el rango de fechas"""
    print(f"\n✅ Verificando rango de fechas: {start_date} a {end_date}")
    
    data = result.get('data', [])
    errors_found = False
    
    for item in data:
        # Intentar obtener la fecha del item
        fecha_str = item.get('fecha') or item.get('fecha_registro')
        if fecha_str:
            try:
                # Parsear la fecha
                from datetime import datetime
                if isinstance(fecha_str, str):
                    if '/' in fecha_str:
                        fecha = datetime.strptime(fecha_str.split()[0], '%d/%m/%Y').date()
                    else:
                        fecha = datetime.fromisoformat(fecha_str).date()
                else:
                    fecha = fecha_str
                
                if start_date and fecha < start_date:
                    print(f"❌ ERROR: Fecha {fecha} es anterior a {start_date}")
                    errors_found = True
                if end_date and fecha > end_date:
                    print(f"❌ ERROR: Fecha {fecha} es posterior a {end_date}")
                    errors_found = True
            except Exception as e:
                pass
    
    if not errors_found:
        print("✅ Todas las fechas están en el rango correcto")

def show_data_statistics():
    """Muestra estadísticas de datos disponibles"""
    print("\n" + "=" * 80)
    print("📊 ESTADÍSTICAS DE DATOS DISPONIBLES")
    print("=" * 80)
    
    # Pedidos
    total_pedidos = Pedido.objects.count()
    pedidos_2024 = Pedido.objects.filter(created_at__year=2024).count()
    pedidos_2025 = Pedido.objects.filter(created_at__year=2025).count()
    
    print(f"\n🛒 PEDIDOS:")
    print(f"  Total: {total_pedidos}")
    print(f"  Año 2024: {pedidos_2024}")
    print(f"  Año 2025: {pedidos_2025}")
    
    if total_pedidos > 0:
        first_pedido = Pedido.objects.order_by('created_at').first()
        last_pedido = Pedido.objects.order_by('-created_at').first()
        print(f"  Primer pedido: {first_pedido.created_at}")
        print(f"  Último pedido: {last_pedido.created_at}")
    
    # Prendas
    total_prendas = Prenda.objects.count()
    print(f"\n📦 PRENDAS:")
    print(f"  Total: {total_prendas}")
    
    # Clientes (Users)
    total_clientes = User.objects.count()
    clientes_2024 = User.objects.filter(created_at__year=2024).count()
    clientes_2025 = User.objects.filter(created_at__year=2025).count()
    
    print(f"\n👥 CLIENTES (USERS):")
    print(f"  Total: {total_clientes}")
    print(f"  Registrados 2024: {clientes_2024}")
    print(f"  Registrados 2025: {clientes_2025}")

def main():
    print("=" * 80)
    print("🧪 TESTING NATURAL LANGUAGE REPORTS")
    print("=" * 80)
    
    # Mostrar estadísticas primero
    show_data_statistics()
    
    # Probar cada ejemplo
    for i, example in enumerate(EXAMPLES, 1):
        print("\n\n")
        print("=" * 80)
        print(f"TEST {i}/{len(EXAMPLES)}")
        print("=" * 80)
        
        try:
            # Parse el prompt
            parsed = test_prompt_parsing(example)
            
            # Ejecutar la query
            result = test_query_execution(parsed)
            
            # Verificar rango de fechas si aplica
            if parsed.get('period'):
                verify_date_range(
                    result, 
                    parsed['period'].get('start_date'), 
                    parsed['period'].get('end_date')
                )
            
            print("\n✅ Test completado")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n\n")
    print("=" * 80)
    print("🏁 TESTING COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    main()
