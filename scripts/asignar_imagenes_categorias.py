#!/usr/bin/env python3
"""
🔗 ASIGNAR IMÁGENES S3 A PRENDAS DE VESTIDOS, JEANS Y JACKETS

Este script asigna las imágenes subidas a S3 a las prendas existentes en la BD.
Similar a asignar_imagenes_blusas.py pero para las 3 categorías nuevas.

Estructura S3: productos/[Categoria]/XXXXXX_1.jpg

Uso:
    python scripts/asignar_imagenes_categorias.py
"""

import os
import sys
import django
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db import transaction
from decouple import config
from apps.products.models import Prenda, ImagenPrendaURL, Categoria

# ============= CONFIGURACIÓN S3 =============
S3_BUCKET = config('AWS_STORAGE_BUCKET_NAME', default='smart-sales-2025-media')
S3_REGION = config('AWS_S3_REGION_NAME', default='us-east-1')
S3_BASE_URL = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com"

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

def generar_urls_imagenes(categoria, cantidad_maxima=2500):
    """
    Genera las URLs de las imágenes de una categoría desde S3.
    
    Args:
        categoria: Nombre de la categoría (Vestidos, Jeans, Jackets)
        cantidad_maxima: Máximo número de imágenes a generar
    
    Returns:
        Lista de URLs
    """
    print(f"{Colors.CYAN}📸 Generando URLs de imágenes de {categoria}...{Colors.END}")
    
    imagenes = []
    for i in range(1, cantidad_maxima + 1):
        numero = str(i).zfill(6)
        key = f"productos/{categoria}/{numero}_1.jpg"
        url = f"{S3_BASE_URL}/{key}"
        imagenes.append(url)
    
    print(f"{Colors.OK}✅ {len(imagenes)} URLs generadas{Colors.END}")
    print(f"{Colors.CYAN}Ejemplo: {imagenes[0]}{Colors.END}")
    return imagenes

def asignar_imagenes_categoria(nombre_categoria, max_imagenes=2500):
    """
    Asigna imágenes de S3 a las prendas de una categoría específica.
    
    Args:
        nombre_categoria: Nombre de la categoría (Vestidos, Jeans, Jackets)
        max_imagenes: Cantidad máxima de imágenes disponibles en S3
    """
    print_header(f"🖼️ ASIGNANDO IMÁGENES A {nombre_categoria.upper()}")
    
    # Verificar que la categoría existe
    try:
        categoria = Categoria.objects.get(nombre__iexact=nombre_categoria)
    except Categoria.DoesNotExist:
        print(f"{Colors.FAIL}❌ Categoría '{nombre_categoria}' no encontrada en BD{Colors.END}")
        return 0, 0, 0
    
    # Obtener prendas de esta categoría
    prendas = Prenda.objects.filter(categorias=categoria).order_by('id')
    total_prendas = prendas.count()
    
    print(f"{Colors.BLUE}📊 Total de {nombre_categoria} en BD: {total_prendas}{Colors.END}")
    
    if total_prendas == 0:
        print(f"{Colors.WARN}⚠️ No se encontraron prendas de {nombre_categoria}{Colors.END}")
        return 0, 0, 0
    
    # Generar URLs de imágenes
    imagenes_urls = generar_urls_imagenes(nombre_categoria, max_imagenes)
    
    # Verificar cuántas prendas ya tienen imágenes
    prendas_con_imagenes = ImagenPrendaURL.objects.filter(
        prenda__in=prendas
    ).values_list('prenda_id', flat=True).distinct()
    
    print(f"{Colors.CYAN}📸 Prendas que ya tienen imágenes: {len(prendas_con_imagenes)}{Colors.END}")
    
    # Contadores
    imagenes_creadas = 0
    imagenes_actualizadas = 0
    errores = 0
    
    print(f"\n{Colors.CYAN}🔄 Procesando {nombre_categoria}...{Colors.END}\n")
    
    with transaction.atomic():
        for idx, prenda in enumerate(prendas, start=0):
            try:
                # Usar el índice para asignar la imagen correspondiente
                if idx < len(imagenes_urls):
                    imagen_url = imagenes_urls[idx]
                else:
                    # Si hay más prendas que imágenes, reciclar imágenes
                    imagen_url = imagenes_urls[idx % len(imagenes_urls)]
                
                # Verificar si ya tiene imagen
                imagen_existente = ImagenPrendaURL.objects.filter(prenda=prenda).first()
                
                if imagen_existente:
                    # Actualizar la URL si es diferente
                    if imagen_existente.imagen_url != imagen_url:
                        imagen_existente.imagen_url = imagen_url
                        imagen_existente.es_principal = True
                        imagen_existente.save()
                        imagenes_actualizadas += 1
                else:
                    # Crear nueva imagen
                    ImagenPrendaURL.objects.create(
                        prenda=prenda,
                        imagen_url=imagen_url,
                        es_principal=True,
                        orden=1,
                        alt_text=prenda.nombre
                    )
                    imagenes_creadas += 1
                
                # Mostrar progreso cada 50 prendas
                if (idx + 1) % 50 == 0:
                    print(f"  [{idx + 1:4d}/{total_prendas}] Procesando...")
                    
            except Exception as e:
                errores += 1
                print(f"{Colors.FAIL}❌ Error en prenda ID {prenda.id}: {e}{Colors.END}")
    
    # Resumen de categoría
    print(f"\n{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"{Colors.OK}✅ Imágenes creadas:      {imagenes_creadas}{Colors.END}")
    print(f"{Colors.CYAN}🔄 Imágenes actualizadas: {imagenes_actualizadas}{Colors.END}")
    print(f"{Colors.FAIL}❌ Errores:               {errores}{Colors.END}")
    print(f"{Colors.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📸 Total procesado:       {imagenes_creadas + imagenes_actualizadas}{Colors.END}\n")
    
    # Mostrar ejemplos
    print(f"{Colors.CYAN}📋 EJEMPLOS DE IMÁGENES ASIGNADAS:{Colors.END}\n")
    ejemplos = ImagenPrendaURL.objects.filter(prenda__in=prendas)[:3]
    for img in ejemplos:
        print(f"  {Colors.GREEN}✓{Colors.END} {img.prenda.nombre}")
        print(f"    {Colors.CYAN}{img.imagen_url}{Colors.END}")
    
    return imagenes_creadas, imagenes_actualizadas, errores

def main():
    print_header("🔗 ASIGNAR IMÁGENES S3 A PRENDAS")
    
    print(f"{Colors.CYAN}🔧 Configuración:{Colors.END}")
    print(f"  Bucket: {S3_BUCKET}")
    print(f"  Base URL: {S3_BASE_URL}")
    print(f"  Categorías a procesar: Vestidos, Jeans, Jackets")
    
    input(f"\n{Colors.WARN}⚠️  Presiona Enter para continuar...{Colors.END}")
    
    # Contadores totales
    total_creadas = 0
    total_actualizadas = 0
    total_errores = 0
    
    # Procesar cada categoría
    categorias = [
        ('Vestidos', 2500),
        ('Jeans', 2500),
        ('Jackets', 2500)
    ]
    
    for categoria, max_imgs in categorias:
        creadas, actualizadas, errores = asignar_imagenes_categoria(categoria, max_imgs)
        total_creadas += creadas
        total_actualizadas += actualizadas
        total_errores += errores
    
    # Resumen final
    print_header("🎉 PROCESO COMPLETADO")
    print(f"{Colors.BOLD}📊 RESUMEN TOTAL:{Colors.END}")
    print(f"{Colors.OK}✅ Total imágenes creadas:      {total_creadas}{Colors.END}")
    print(f"{Colors.CYAN}🔄 Total imágenes actualizadas: {total_actualizadas}{Colors.END}")
    print(f"{Colors.FAIL}❌ Total errores:               {total_errores}{Colors.END}")
    print(f"\n{Colors.GREEN}✨ ¡Asignación completada!{Colors.END}")
    
    # Verificar totales por categoría
    print(f"\n{Colors.CYAN}📊 PRENDAS CON IMÁGENES POR CATEGORÍA:{Colors.END}\n")
    
    for cat_nombre in ['Blusas', 'Vestidos', 'Jeans', 'Jackets']:
        try:
            cat = Categoria.objects.get(nombre__iexact=cat_nombre)
            prendas_cat = Prenda.objects.filter(categorias=cat)
            con_img = prendas_cat.filter(imagenes_url__isnull=False).distinct().count()
            total = prendas_cat.count()
            porcentaje = (con_img / total * 100) if total > 0 else 0
            
            print(f"  {Colors.GREEN}{cat_nombre:12}{Colors.END}: {con_img:4d}/{total:4d} ({porcentaje:.1f}%)")
        except:
            pass
    
    print(f"\n{Colors.BOLD}✅ ¡Recarga el frontend para ver los cambios!{Colors.END}\n")

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
