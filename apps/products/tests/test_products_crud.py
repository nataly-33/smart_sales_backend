#!/usr/bin/env python
"""
Script de Validación Completo: CRUD de Productos con Stocks

Ejecuta: python test_products_crud.py

Verifica:
- CREATE: Crear producto con tallas y stocks
- READ: Obtener producto con todos sus datos
- UPDATE: Actualizar producto, tallas y stocks
- DELETE: Eliminar producto (soft delete)
- Coherencia: Datos guardados matchean datos enviados
"""

import os
import sys
import django
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from apps.products.models import Prenda, Categoria, Marca, Talla, StockPrenda
from apps.accounts.models import Role

User = get_user_model()

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BLUE}{BOLD}{'='*70}{RESET}")
    print(f"{BLUE}{BOLD}{text:^70}{RESET}")
    print(f"{BLUE}{BOLD}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def cleanup():
    """Limpiar datos de prueba"""
    print_info("Limpiando datos de prueba...")
    Prenda.objects.filter(nombre__startswith="TEST_").delete()

def setup_test_data():
    """Crear datos necesarios para las pruebas"""
    print_info("Configurando datos de prueba...")
    
    # Obtener o crear categoria
    categoria, _ = Categoria.objects.get_or_create(
        nombre="Categoría Test",
        defaults={'descripcion': 'Categoría para testing'}
    )
    
    # Obtener o crear marca
    marca, _ = Marca.objects.get_or_create(
        nombre="Marca Test",
        defaults={'descripcion': 'Marca para testing'}
    )
    
    # Obtener tallas existentes
    talla_m = Talla.objects.filter(nombre='M').first()
    talla_l = Talla.objects.filter(nombre='L').first()
    
    if not talla_m or not talla_l:
        print_error("Las tallas M y L no existen. Crea al menos esas tallas en la BD.")
        return None
    
    return {
        'categoria': categoria,
        'marca': marca,
        'talla_m': talla_m,
        'talla_l': talla_l,
    }

def test_create_product(test_data):
    """Test 1: CREATE - Crear producto con stocks"""
    print_header("TEST 1: CREATE - Crear Producto con Stocks")
    
    try:
        # Crear producto
        prenda = Prenda.objects.create(
            nombre="TEST_Vestido Elegante",
            descripcion="Vestido de prueba con stocks",
            precio=Decimal('99.99'),
            marca=test_data['marca'],
            color="Rojo",
            material="Algodón 100%",
            activa=True,
            destacada=True,
            es_novedad=True,
        )
        print_success(f"Producto creado: {prenda.id}")
        
        # Asignar categorías y tallas
        prenda.categorias.add(test_data['categoria'])
        prenda.tallas_disponibles.add(test_data['talla_m'], test_data['talla_l'])
        print_success(f"Categorías y tallas asignadas")
        
        # Crear stocks
        stock_m = StockPrenda.objects.create(
            prenda=prenda,
            talla=test_data['talla_m'],
            cantidad=20,
            stock_minimo=5,
        )
        print_success(f"Stock M creado: cantidad={stock_m.cantidad}, mín={stock_m.stock_minimo}")
        
        stock_l = StockPrenda.objects.create(
            prenda=prenda,
            talla=test_data['talla_l'],
            cantidad=15,
            stock_minimo=5,
        )
        print_success(f"Stock L creado: cantidad={stock_l.cantidad}, mín={stock_l.stock_minimo}")
        
        # Validar totales
        assert prenda.stock_total == 35, f"Stock total debe ser 35, pero es {prenda.stock_total}"
        print_success(f"Stock total validado: {prenda.stock_total}")
        
        return prenda
        
    except Exception as e:
        print_error(f"Error al crear producto: {e}")
        return None

def test_read_product(prenda):
    """Test 2: READ - Obtener producto con stocks"""
    print_header("TEST 2: READ - Obtener Producto con Datos Completos")
    
    try:
        # Recargar desde BD
        prenda_db = Prenda.objects.get(id=prenda.id)
        print_success(f"Producto obtenido: {prenda_db.nombre}")
        
        # Verificar campos
        assert prenda_db.nombre == "TEST_Vestido Elegante", "Nombre no coincide"
        print_success("✓ Nombre correcto")
        
        assert prenda_db.precio == Decimal('99.99'), "Precio no coincide"
        print_success("✓ Precio correcto")
        
        assert prenda_db.color == "Rojo", "Color no coincide"
        print_success("✓ Color correcto")
        
        assert prenda_db.activa == True, "Activa debe ser True"
        print_success("✓ Estado activo correcto")
        
        # Verificar relaciones
        categorias = list(prenda_db.categorias.values_list('nombre', flat=True))
        assert 'Categoría Test' in categorias, "Categoría no asignada"
        print_success(f"✓ Categorías: {categorias}")
        
        tallas = list(prenda_db.tallas_disponibles.values_list('nombre', flat=True))
        assert 'M' in tallas and 'L' in tallas, "Tallas no asignadas"
        print_success(f"✓ Tallas: {tallas}")
        
        # Verificar stocks
        stocks = list(prenda_db.stocks.all())
        assert len(stocks) == 2, f"Debe haber 2 stocks, pero hay {len(stocks)}"
        print_success(f"✓ Cantidad de stocks: {len(stocks)}")
        
        for stock in stocks:
            print_info(f"  - {stock.talla.nombre}: cantidad={stock.cantidad}, mín={stock.stock_minimo}")
        
        # Verificar stock total
        assert prenda_db.stock_total == 35, f"Stock total debe ser 35, pero es {prenda_db.stock_total}"
        print_success(f"✓ Stock total: {prenda_db.stock_total}")
        
        return prenda_db
        
    except Exception as e:
        print_error(f"Error al leer producto: {e}")
        return None

def test_update_product(prenda):
    """Test 3: UPDATE - Actualizar producto y stocks"""
    print_header("TEST 3: UPDATE - Actualizar Producto y Stocks")
    
    try:
        # Actualizar campos básicos
        prenda.nombre = "TEST_Vestido Elegante v2"
        prenda.precio = Decimal('119.99')
        prenda.material = "Algodón 100% - Premium"
        prenda.save()
        print_success("Campos básicos actualizados")
        
        # Actualizar cantidad de stock M
        stock_m = prenda.stocks.get(talla__nombre='M')
        stock_m.cantidad = 30
        stock_m.stock_minimo = 8
        stock_m.save()
        print_success(f"Stock M actualizado: cantidad={stock_m.cantidad}, mín={stock_m.stock_minimo}")
        
        # Actualizar cantidad de stock L
        stock_l = prenda.stocks.get(talla__nombre='L')
        stock_l.cantidad = 25
        stock_l.stock_minimo = 10
        stock_l.save()
        print_success(f"Stock L actualizado: cantidad={stock_l.cantidad}, mín={stock_l.stock_minimo}")
        
        # Verificar cambios
        prenda_db = Prenda.objects.get(id=prenda.id)
        assert prenda_db.nombre == "TEST_Vestido Elegante v2", "Nombre no actualizado"
        print_success("✓ Nombre actualizado correctamente")
        
        assert prenda_db.precio == Decimal('119.99'), "Precio no actualizado"
        print_success("✓ Precio actualizado correctamente")
        
        assert prenda_db.stock_total == 55, f"Stock total debe ser 55, pero es {prenda_db.stock_total}"
        print_success(f"✓ Stock total actualizado: {prenda_db.stock_total}")
        
        return prenda_db
        
    except Exception as e:
        print_error(f"Error al actualizar producto: {e}")
        return None

def test_update_stocks_with_new_talla(prenda, test_data):
    """Test 4: UPDATE - Agregar nueva talla y remover una"""
    print_header("TEST 4: UPDATE AVANZADO - Cambiar Tallas y Stocks")
    
    try:
        # Obtener otra talla
        talla_s = Talla.objects.filter(nombre='S').first()
        if not talla_s:
            print_warning("Talla S no existe, saltando este test")
            return prenda
        
        # Remover talla L y agregar talla S
        prenda.tallas_disponibles.remove(test_data['talla_l'])
        prenda.tallas_disponibles.add(talla_s)
        print_success("Talla L removida, talla S agregada")
        
        # Eliminar stock L
        prenda.stocks.filter(talla__nombre='L').delete()
        print_success("Stock L eliminado")
        
        # Crear stock S
        stock_s = StockPrenda.objects.create(
            prenda=prenda,
            talla=talla_s,
            cantidad=10,
            stock_minimo=3,
        )
        print_success(f"Stock S creado: cantidad={stock_s.cantidad}, mín={stock_s.stock_minimo}")
        
        # Verificar cambios
        prenda_db = Prenda.objects.get(id=prenda.id)
        stocks = list(prenda_db.stocks.all().values_list('talla__nombre', 'cantidad'))
        print_success(f"Stocks finales: {stocks}")
        
        tallas_final = list(prenda_db.tallas_disponibles.values_list('nombre', flat=True))
        assert 'L' not in tallas_final and 'S' in tallas_final, "Tallas no actualizadas correctamente"
        print_success(f"✓ Tallas finales: {tallas_final}")
        
        assert prenda_db.stock_total == 40, f"Stock total debe ser 40 (30+10), pero es {prenda_db.stock_total}"
        print_success(f"✓ Stock total correcto: {prenda_db.stock_total}")
        
        return prenda_db
        
    except Exception as e:
        print_error(f"Error en update avanzado: {e}")
        return None

def test_soft_delete(prenda):
    """Test 5: DELETE - Soft delete (marca como eliminado)"""
    print_header("TEST 5: DELETE - Soft Delete de Producto")
    
    try:
        prenda_id = prenda.id
        
        # Perform soft delete
        prenda.soft_delete()
        print_success(f"Producto marcado como eliminado (soft delete)")
        
        # Verificar que sigue en BD pero con deleted_at
        prenda_db = Prenda.objects.filter(id=prenda_id, deleted_at__isnull=False).first()
        assert prenda_db is not None, "Producto no encontrado con deleted_at"
        print_success("✓ Producto encontrado con deleted_at set")
        
        # Verificar que no aparece en listados activos
        count_active = Prenda.objects.filter(id=prenda_id, deleted_at__isnull=True).count()
        assert count_active == 0, "Producto eliminado aparece en listado activo"
        print_success("✓ Producto no aparece en listado activo")
        
        # Los stocks deberían seguir existiendo (relación en cascade)
        stocks_count = StockPrenda.objects.filter(prenda_id=prenda_id).count()
        print_success(f"✓ Stocks del producto eliminado: {stocks_count}")
        
        return True
        
    except Exception as e:
        print_error(f"Error en soft delete: {e}")
        return False

def test_serializer_output(prenda):
    """Test 6: SERIALIZER - Verificar que GET retorna datos correctos"""
    print_header("TEST 6: VALIDACIÓN - Serializer OUTPUT")
    
    try:
        from apps.products.serializers import PrendaDetailSerializer
        
        serializer = PrendaDetailSerializer(prenda)
        data = serializer.data
        
        print_info("Verificando estructura de respuesta...")
        
        # Verificar campos básicos
        assert data['nombre'], "nombre está vacío"
        print_success("✓ nombre presente")
        
        assert data['precio'], "precio está vacío"
        print_success("✓ precio presente")
        
        # Verificar stocks con talla_detalle
        stocks = data.get('stocks', [])
        assert len(stocks) > 0, "stocks vacío"
        print_success(f"✓ stocks presente: {len(stocks)} items")
        
        for stock in stocks:
            assert 'talla' in stock, "stock sin 'talla'"
            assert 'cantidad' in stock, "stock sin 'cantidad'"
            assert 'stock_minimo' in stock, "stock sin 'stock_minimo'"
            assert 'talla_detalle' in stock, "stock sin 'talla_detalle'"
            print_success(f"  ✓ Stock {stock['talla_detalle']['nombre']}: cantidad={stock['cantidad']}")
        
        # Verificar categorías
        categorias = data.get('categorias_detalle', [])
        assert len(categorias) > 0, "categorías_detalle vacío"
        print_success(f"✓ categorías_detalle: {len(categorias)} items")
        
        # Verificar tallas
        tallas = data.get('tallas_disponibles_detalle', [])
        assert len(tallas) > 0, "tallas_disponibles_detalle vacío"
        print_success(f"✓ tallas_disponibles_detalle: {len(tallas)} items")
        
        # Verificar propiedades calculadas
        assert 'stock_total' in data, "stock_total ausente"
        print_success(f"✓ stock_total: {data['stock_total']}")
        
        return True
        
    except Exception as e:
        print_error(f"Error en validación de serializer: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests"""
    print_header("🧪 TEST SUITE: CRUD DE PRODUCTOS CON STOCKS")
    
    # Limpiar datos previos
    cleanup()
    
    # Setup
    test_data = setup_test_data()
    if not test_data:
        print_error("No se pudo configurar datos de prueba")
        return False
    
    # Ejecutar tests
    results = []
    
    # Test 1: Create
    prenda = test_create_product(test_data)
    results.append(("CREATE", prenda is not None))
    
    if not prenda:
        print_error("No se puede continuar sin producto creado")
        cleanup()
        return False
    
    # Test 2: Read
    prenda = test_read_product(prenda)
    results.append(("READ", prenda is not None))
    
    if not prenda:
        cleanup()
        return False
    
    # Test 3: Update
    prenda = test_update_product(prenda)
    results.append(("UPDATE", prenda is not None))
    
    if not prenda:
        cleanup()
        return False
    
    # Test 4: Update avanzado
    prenda = test_update_stocks_with_new_talla(prenda, test_data)
    results.append(("UPDATE AVANZADO", prenda is not None))
    
    # Test 5: Serializer
    serializer_ok = test_serializer_output(prenda)
    results.append(("SERIALIZER", serializer_ok))
    
    # Test 6: Soft Delete
    delete_ok = test_soft_delete(prenda)
    results.append(("DELETE", delete_ok))
    
    # Resultados finales
    print_header("📊 RESULTADOS FINALES")
    
    all_passed = True
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
            all_passed = False
    
    # Cleanup
    cleanup()
    
    if all_passed:
        print(f"\n{GREEN}{BOLD}🎉 TODOS LOS TESTS PASARON ✅{RESET}\n")
        return True
    else:
        print(f"\n{RED}{BOLD}⚠️  ALGUNOS TESTS FALLARON ❌{RESET}\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
