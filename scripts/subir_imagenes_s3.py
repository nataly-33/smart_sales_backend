#!/usr/bin/env python3
"""
📤 SUBIR IMÁGENES DE CATEGORÍAS A S3

Este script sube imágenes de Jeans, Vestidos y Jackets a S3 desde los datasets locales.
Estructura en S3: productos/[Categoria]/XXXXXX_1.jpg

Datasets:
1. Dataset mixto: D:\1NATALY\SISTEMAS DE INFORMACIÓN II\ropa\images (filtrar con styles.csv)
2. Dataset jeans: D:\1NATALY\SISTEMAS DE INFORMACIÓN II\ropa\jeans_images

Uso:
    python scripts/subir_imagenes_s3.py
"""

import os
import sys
import csv
import boto3
from pathlib import Path
from PIL import Image
from io import BytesIO
import time

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from decouple import config

# ============= CONFIGURACIÓN S3 =============
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')

# Rutas locales
DATASET_MIXTO = Path(r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\ropa\images")
CSV_MIXTO = Path(r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\ropa\styles.csv")
DATASET_JEANS = Path(r"D:\1NATALY\SISTEMAS DE INFORMACIÓN II\ropa\jeans_images")

# ============= COLORES =============
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    OK = '\033[92m'

def print_header(text):
    print(f"\n{Colors.HEADER}{'=' * 80}")
    print(f"{text:^80}")
    print(f"{'=' * 80}{Colors.END}\n")

# ============= CLIENTE S3 =============
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION
)

def filtrar_imagenes_csv(categoria_filtro):
    """
    Filtra imágenes del dataset mixto según el CSV.
    
    Categorías a buscar:
    - Jeans: articleType contiene 'Jeans'
    - Vestidos: articleType contiene 'Dresses' o 'Gowns'
    - Jackets: articleType contiene 'Jackets', 'Coats', 'Blazers'
    
    Solo mujeres: gender = 'Women'
    """
    print(f"{Colors.CYAN}📋 Filtrando imágenes de {categoria_filtro} del CSV...{Colors.END}")
    
    mapeo_categorias = {
        'Jeans': ['Jeans'],
        'Vestidos': ['Dresses', 'Gowns', 'Dress'],
        'Jackets': ['Jackets', 'Coats', 'Blazers', 'Jacket', 'Coat', 'Blazer']
    }
    
    articulos_validos = mapeo_categorias.get(categoria_filtro, [])
    imagenes_filtradas = []
    
    try:
        with open(CSV_MIXTO, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Filtrar por género (solo mujeres) y tipo de artículo
                if row['gender'] == 'Women':
                    article_type = row['articleType']
                    if any(articulo.lower() in article_type.lower() for articulo in articulos_validos):
                        image_id = row['id']
                        image_path = DATASET_MIXTO / f"{image_id}.jpg"
                        if image_path.exists():
                            imagenes_filtradas.append(image_path)
        
        print(f"{Colors.OK}✅ {len(imagenes_filtradas)} imágenes de {categoria_filtro} encontradas{Colors.END}")
        return imagenes_filtradas
    
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error leyendo CSV: {e}{Colors.END}")
        return []

def obtener_imagenes_jeans_directas():
    """
    Obtiene todas las imágenes del dataset específico de jeans.
    """
    print(f"{Colors.CYAN}📂 Buscando imágenes en dataset directo de jeans...{Colors.END}")
    
    imagenes = []
    if DATASET_JEANS.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
            imagenes.extend(DATASET_JEANS.glob(ext))
    
    print(f"{Colors.OK}✅ {len(imagenes)} imágenes directas de jeans encontradas{Colors.END}")
    return imagenes

def optimizar_imagen(image_path):
    """
    Optimiza la imagen antes de subirla (resize si es muy grande, comprimir).
    """
    try:
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar si es muy grande (max 1200px en el lado más largo)
            max_size = 1200
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Guardar en memoria optimizado
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            return buffer
    
    except Exception as e:
        print(f"{Colors.WARN}⚠️ Error optimizando {image_path.name}: {e}{Colors.END}")
        return None

def subir_imagenes_categoria(categoria, imagenes_paths, max_imagenes=2500):
    """
    Sube las imágenes de una categoría a S3 con nombres ordenados.
    
    Estructura: productos/[Categoria]/XXXXXX_1.jpg
    """
    print(f"\n{Colors.BLUE}📤 Subiendo imágenes de {categoria} a S3...{Colors.END}")
    
    subidas_exitosas = 0
    errores = 0
    omitidas = 0
    
    # Limitar cantidad si hay muchas
    imagenes_a_subir = imagenes_paths[:max_imagenes]
    total = len(imagenes_a_subir)
    
    print(f"{Colors.CYAN}Total a subir: {total} imágenes{Colors.END}\n")
    
    for idx, image_path in enumerate(imagenes_a_subir, start=1):
        try:
            # Generar nombre en S3: 000001_1.jpg, 000002_1.jpg, etc.
            numero = str(idx).zfill(6)
            s3_key = f"productos/{categoria}/{numero}_1.jpg"
            
            # Verificar si ya existe en S3
            try:
                s3_client.head_object(Bucket=S3_BUCKET, Key=s3_key)
                omitidas += 1
                if idx % 100 == 0:
                    print(f"  [{idx:4d}/{total}] Ya existe: {s3_key}")
                continue
            except:
                pass  # No existe, continuar con la subida
            
            # Optimizar imagen
            buffer = optimizar_imagen(image_path)
            if not buffer:
                errores += 1
                continue
            
            # Subir a S3
            s3_client.upload_fileobj(
                buffer,
                S3_BUCKET,
                s3_key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'CacheControl': 'max-age=31536000',
                }
            )
            
            subidas_exitosas += 1
            
            # Mostrar progreso cada 50 imágenes
            if idx % 50 == 0:
                print(f"  [{idx:4d}/{total}] ✅ Subido: {s3_key}")
            
            # Pequeña pausa para no saturar S3
            if idx % 100 == 0:
                time.sleep(0.5)
        
        except Exception as e:
            errores += 1
            print(f"{Colors.FAIL}  ❌ Error en {image_path.name}: {e}{Colors.END}")
    
    # Resumen de categoría
    print(f"\n{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{Colors.OK}✅ Subidas exitosas: {subidas_exitosas}{Colors.END}")
    print(f"{Colors.CYAN}⏭️  Omitidas (ya existían): {omitidas}{Colors.END}")
    print(f"{Colors.FAIL}❌ Errores: {errores}{Colors.END}")
    print(f"{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}\n")
    
    return subidas_exitosas

def main():
    print_header("📤 SUBIR IMÁGENES DE CATEGORÍAS A S3")
    
    print(f"{Colors.CYAN}🔧 Configuración:{Colors.END}")
    print(f"  Bucket: {S3_BUCKET}")
    print(f"  Región: {S3_REGION}")
    print(f"  Dataset mixto: {DATASET_MIXTO}")
    print(f"  Dataset jeans: {DATASET_JEANS}")
    
    input(f"\n{Colors.WARN}⚠️  Presiona Enter para continuar...{Colors.END}")
    
    total_subidas = 0
    
    # ============= 1. VESTIDOS =============
    print_header("👗 PROCESANDO VESTIDOS")
    imagenes_vestidos = filtrar_imagenes_csv('Vestidos')
    if imagenes_vestidos:
        subidas = subir_imagenes_categoria('Vestidos', imagenes_vestidos)
        total_subidas += subidas
    
    # ============= 2. JEANS (Mixto + Directo) =============
    print_header("👖 PROCESANDO JEANS")
    
    # Combinar ambas fuentes de jeans
    imagenes_jeans_csv = filtrar_imagenes_csv('Jeans')
    imagenes_jeans_directas = obtener_imagenes_jeans_directas()
    
    todas_jeans = imagenes_jeans_csv + imagenes_jeans_directas
    print(f"{Colors.BOLD}📊 Total jeans combinadas: {len(todas_jeans)}{Colors.END}")
    
    if todas_jeans:
        subidas = subir_imagenes_categoria('Jeans', todas_jeans)
        total_subidas += subidas
    
    # ============= 3. JACKETS =============
    print_header("🧥 PROCESANDO JACKETS")
    imagenes_jackets = filtrar_imagenes_csv('Jackets')
    if imagenes_jackets:
        subidas = subir_imagenes_categoria('Jackets', imagenes_jackets)
        total_subidas += subidas
    
    # ============= RESUMEN FINAL =============
    print_header("🎉 PROCESO COMPLETADO")
    print(f"{Colors.OK}✅ Total de imágenes subidas: {total_subidas}{Colors.END}")
    print(f"\n{Colors.CYAN}Estructura en S3:{Colors.END}")
    print(f"  📁 productos/")
    print(f"    📁 Blusas/ (existentes)")
    print(f"    📁 Vestidos/ (nuevas)")
    print(f"    📁 Jeans/ (nuevas)")
    print(f"    📁 Jackets/ (nuevas)")
    
    print(f"\n{Colors.GREEN}✨ ¡Listo para ejecutar el script de asignación!{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARN}⚠️ Proceso interrumpido por el usuario{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ ERROR: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
