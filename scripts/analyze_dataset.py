#!/usr/bin/env python3
"""
Analiza el dataset local para entender su estructura
Genera reporte con:
- Total de imágenes
- Patrones de nombres
- Categorías propuestas
- Marcas asignadas
"""

import os
from pathlib import Path
from collections import Counter
import json
import re

DATASET_PATH = r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\nuevo GESTION_DOCUMENTAL\smartsales\clothes"

def analizar_dataset():
    """Analiza la estructura del dataset"""
    
    dataset_dir = Path(DATASET_PATH)
    
    if not dataset_dir.exists():
        print(f"❌ ERROR: No se encuentra la carpeta: {DATASET_PATH}")
        print(f"   Verifica que la ruta sea correcta")
        return
    
    # Obtener todas las imágenes
    extensiones_validas = {'.jpg', '.jpeg', '.png', '.webp'}
    imagenes = [
        f for f in dataset_dir.iterdir()
        if f.is_file() and f.suffix.lower() in extensiones_validas
    ]
    
    if not imagenes:
        print(f"❌ ERROR: No se encontraron imágenes en {DATASET_PATH}")
        print(f"   Extensiones válidas: {extensiones_validas}")
        return
    
    print(f"\n📊 ANÁLISIS DEL DATASET")
    print(f"{'='*70}")
    print(f"📁 Ruta: {DATASET_PATH}")
    print(f"📷 Total de imágenes: {len(imagenes)}")
    
    # Analizar nombres
    nombres = [f.stem for f in imagenes]
    prefijos = Counter()
    suffijos = Counter()
    extensiones = Counter()
    
    for nombre in nombres:
        # Extraer prefijo (antes del número)
        match = re.match(r'^([a-zA-Z_]+)(_|\d)', nombre)
        if match:
            prefijo = match.group(1)
            prefijos[prefijo] += 1
        
        # Extraer sufijo (después del guion bajo o número)
        match = re.search(r'([a-zA-Z_]+)$', nombre)
        if match:
            suffijos[match.group(1)] += 1
    
    for f in imagenes:
        extensiones[f.suffix.lower()] += 1
    
    print(f"\n📸 EXTENSIONES ENCONTRADAS:")
    for ext, count in extensiones.most_common():
        print(f"  • {ext}: {count} imágenes ({count/len(imagenes)*100:.1f}%)")
    
    print(f"\n🏷️  TOP 20 PREFIJOS DETECTADOS:")
    for prefijo, count in prefijos.most_common(20):
        pct = count/len(imagenes)*100
        print(f"  • {prefijo:20} : {count:5} imágenes ({pct:5.1f}%)")
    
    print(f"\n📝 PRIMEROS 10 EJEMPLOS DE NOMBRES:")
    for i, nombre in enumerate(sorted(nombres)[:10], 1):
        print(f"  {i}. {nombre}")
    
    print(f"\n📝 ÚLTIMOS 10 EJEMPLOS DE NOMBRES:")
    for i, nombre in enumerate(sorted(nombres)[-10:], 1):
        print(f"  {i}. {nombre}")
    
    # Crear mapeo automático
    mapeo = {}
    for prefijo, _ in prefijos.most_common():
        if prefijo not in mapeo:
            # Asignar categoría basada en palabras clave
            prefijo_lower = prefijo.lower()
            if any(x in prefijo_lower for x in ['dress', 'gown', 'vestido']):
                mapeo[prefijo] = 'Vestidos'
            elif any(x in prefijo_lower for x in ['shirt', 'blouse', 'top', 'tshirt', 'camisa']):
                mapeo[prefijo] = 'Blusas'
            elif any(x in prefijo_lower for x in ['pants', 'trouser', 'jeans', 'pantalon']):
                mapeo[prefijo] = 'Pantalones'
            elif any(x in prefijo_lower for x in ['skirt', 'falda']):
                mapeo[prefijo] = 'Faldas'
            elif any(x in prefijo_lower for x in ['jacket', 'coat', 'chaqueta']):
                mapeo[prefijo] = 'Chaquetas'
            elif any(x in prefijo_lower for x in ['sweater', 'jumper', 'sueter']):
                mapeo[prefijo] = 'Suéteres'
            elif any(x in prefijo_lower for x in ['shoe', 'boot', 'sandal', 'zapato']):
                mapeo[prefijo] = 'Zapatos'
            else:
                mapeo[prefijo] = 'Otros'
    
    print(f"\n🔄 MAPEO PROPUESTO (prefijo → categoría):")
    print(f"{'  Prefijo':<25} {'Categoría':<20} {'Imágenes':<10} {'%':<8}")
    print(f"  {'-'*60}")
    for prefijo, categoria in sorted(mapeo.items()):
        count = prefijos.get(prefijo, 0)
        pct = count/len(imagenes)*100 if len(imagenes) > 0 else 0
        print(f"  {prefijo:<25} {categoria:<20} {count:<10} {pct:>6.1f}%")
    
    # Guardar mapeo en JSON
    mapeo_file = Path(__file__).parent / 'dataset_mapping.json'
    with open(mapeo_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_imagenes': len(imagenes),
            'dataset_path': DATASET_PATH,
            'mapeo_categorias': mapeo,
            'prefijos': dict(prefijos),
            'extensiones': dict(extensiones),
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Mapeo guardado en: {mapeo_file}")
    
    # Estadísticas por categoría propuesta
    categorias_count = Counter()
    for nombre in nombres:
        match = re.match(r'^([a-zA-Z_]+)', nombre)
        if match:
            prefijo = match.group(1)
            categoria = mapeo.get(prefijo, 'Otros')
            categorias_count[categoria] += 1
    
    print(f"\n📊 DISTRIBUCIÓN POR CATEGORÍA PROPUESTA:")
    print(f"{'  Categoría':<20} {'Imágenes':<10} {'% del Total':<12}")
    print(f"  {'-'*40}")
    total_asignadas = sum(categorias_count.values())
    for categoria in sorted(categorias_count.keys(), key=lambda x: categorias_count[x], reverse=True):
        count = categorias_count.get(categoria, 0)
        pct = count/len(imagenes)*100 if len(imagenes) > 0 else 0
        print(f"  {categoria:<20} {count:<10} {pct:>10.1f}%")
    
    print(f"\n{'='*70}")
    print(f"✅ ANÁLISIS COMPLETADO")
    print(f"{'='*70}\n")
    
    # Mostrar comandos siguientes
    print("📋 PRÓXIMOS PASOS:")
    print("  1. Verificar que el mapeo es correcto")
    print("  2. Ejecutar prueba piloto con 100 imágenes:")
    print("     python scripts/upload_to_s3_v2.py --max-imagenes 100")
    print("  3. Si todo va bien, subir 2500 imágenes:")
    print("     python scripts/upload_to_s3_v2.py --max-imagenes 2500 --lote-size 100")
    print()

if __name__ == '__main__':
    analizar_dataset()
